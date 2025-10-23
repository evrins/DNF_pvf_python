"""
Optimized PVF Reader for DNF Package Tool

This module provides classes and functions to read and parse PVF (Package Virtual File) format
used in Dungeon & Fighter game files.

PVF Structure:
- Header: Unencrypted, contains file tree encryption key
- FileTree: Encrypted using header key, contains file sizes, offsets, paths, and keys
- Data: File data encrypted with individual keys

Key file types:
- stringtable.bin: Contains all text fields, other files store text field indices
- n_string.lst: Contains paths to str files
- *.str: StringTable equivalent text replacements
- *.lst: ID lists mapping item IDs to item files
- *.stk: Item files, decrypted and read byte by byte
"""

import json
import logging
import struct
from dataclasses import dataclass
from pathlib import Path
from struct import unpack
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from zhconv import convert
except ImportError:

    def convert(text: str, target: str) -> str:
        return text


try:
    import ctypes

    # Load the DLL for faster decryption
    dll_path = './DLL1.dll'
    dll = ctypes.CDLL(dll_path)
    unpackHeaderTree = dll.unpackHeaderTree
    unpackHeaderTree.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_int,
        ctypes.c_uint32,
    )
    unpackHeaderTree.restype = None
    HAS_DLL = True
except (OSError, AttributeError):
    HAS_DLL = False

# Configure logging
logger = logging.getLogger(__name__)


# Load configuration
def load_config() -> Tuple[List[str], Dict[str, Any]]:
    """Load keywords and keywords dictionary from config files."""
    keywords = []
    keywords_dict = {}

    keywords_path = Path('./config/pvfKeywords.json')
    if keywords_path.exists():
        try:
            # Try UTF-8 first, then fallback to other encodings
            for encoding in ['utf-8', 'gbk', 'big5', 'latin1']:
                try:
                    with open(keywords_path, 'r', encoding=encoding) as f:
                        keywords = json.load(f)
                    break
                except UnicodeDecodeError:
                    continue
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f'Failed to load keywords: {e}')

    keywords_dict_path = Path('./config/pvfKeywordsDict.json')
    if keywords_dict_path.exists():
        try:
            # Try UTF-8 first, then fallback to other encodings
            for encoding in ['utf-8', 'gbk', 'big5', 'latin1']:
                try:
                    with open(keywords_dict_path, 'r', encoding=encoding) as f:
                        keywords_dict = json.load(f)
                    break
                except UnicodeDecodeError:
                    continue
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f'Failed to load keywords dict: {e}')

    return keywords, keywords_dict


KEYWORDS, KEYWORDS_DICT = load_config()


@dataclass
class FileLeaf:
    """Represents a file entry in the PVF file tree."""

    index: int
    fn: int
    file_path: str
    file_length: int
    file_crc32: int
    relative_offset: int
    content: bytes = b''


class CryptoUtils:
    """Utility class for encryption/decryption operations."""

    @staticmethod
    def decrypt_bytes(input_bytes: bytes, crc: int) -> bytes:
        """Decrypt bytes using CRC-based XOR encryption."""
        if not input_bytes:
            return b''

        key = 0x81A79011
        xor = crc ^ key
        int_num = len(input_bytes) // 4

        if int_num == 0:
            return input_bytes

        key_all = xor.to_bytes(4, 'little') * int_num
        value_xored_all = int.from_bytes(key_all, 'little') ^ int.from_bytes(
            input_bytes[: int_num * 4], 'little'
        )

        mask_1 = 0b00000000_00000000_00000000_00111111
        mask_2 = 0b11111111_11111111_11111111_11000000
        mask_1_all = int.from_bytes(mask_1.to_bytes(4, 'little') * int_num, 'little')
        mask_2_all = int.from_bytes(mask_2.to_bytes(4, 'little') * int_num, 'little')

        value_1 = value_xored_all & mask_1_all
        value_2 = value_xored_all & mask_2_all
        value = value_1 << 26 | value_2 >> 6

        return value.to_bytes(4 * int_num, 'little')

    @staticmethod
    def decrypt_bytes_fast(input_bytes: bytes, crc32: int) -> bytes:
        """Fast decryption using DLL if available."""
        if not HAS_DLL:
            return CryptoUtils.decrypt_bytes(input_bytes, crc32)

        file_len = len(input_bytes)
        byte_arr_c = (ctypes.c_uint8 * file_len)(*input_bytes)
        unpackHeaderTree(byte_arr_c, file_len, crc32)
        return bytearray(byte_arr_c)


class PVFHeader:
    """Represents the header of a PVF file."""

    def __init__(self, path: Union[str, Path], read_full_file: bool = False):
        self.pvf_path = Path(path)
        self._fp = None
        self._full_file = None
        self.index = 0  # Pointer for reading HeaderTree

        self._read_header(read_full_file)

    def _read_header(self, read_full_file: bool):
        """Read and parse the PVF header."""
        with open(self.pvf_path, 'rb') as fp:
            # Read header fields
            self.uuid_len = struct.unpack('i', fp.read(4))[0]
            self.uuid = fp.read(self.uuid_len)
            self.pvf_version = struct.unpack('i', fp.read(4))[0]
            self.dir_tree_length = struct.unpack('i', fp.read(4))[0]
            self.dir_tree_crc32 = struct.unpack('I', fp.read(4))[0]
            self.num_files_in_dir_tree = struct.unpack('I', fp.read(4))[0]
            self.file_pack_index_shift = fp.tell() + self.dir_tree_length
            self.header_length = fp.tell()

            # Read and decrypt file tree
            header_tree_bytes = fp.read(self.dir_tree_length)
            self.unpacked_header_tree_decrypted = CryptoUtils.decrypt_bytes_fast(
                header_tree_bytes, self.dir_tree_crc32
            )

            if read_full_file:
                self._full_file = fp.read()

    def get_header_tree_bytes(self, byte_num: int = 4) -> bytes:
        """Get bytes from the decrypted header tree."""
        result = self.unpacked_header_tree_decrypted[self.index : self.index + byte_num]
        self.index += byte_num
        return result

    def read_bytes(self, start_index: int, length: int) -> bytes:
        """Read bytes from the PVF file at specified position."""
        if self._full_file is not None:
            return self._full_file[start_index : start_index + length]

        if self._fp is None:
            self._fp = open(self.pvf_path, 'rb')

        self._fp.seek(start_index)
        return self._fp.read(length)

    def to_bytes(
            self,
            crc: int,
            file_num: int = 0,
            tree_length: int = 0,
            uuid: bytes = b'\x00' * 36,
    ) -> bytes:
        """Convert header to bytes representation."""
        if file_num == 0:
            file_num = self.num_files_in_dir_tree
        if tree_length == 0:
            tree_length = self.dir_tree_length

        result = bytearray()
        result += len(uuid).to_bytes(4, 'little')
        result += uuid
        result += self.pvf_version.to_bytes(4, 'little')
        result += tree_length.to_bytes(4, 'little')
        result += crc.to_bytes(4, 'little')
        result += file_num.to_bytes(4, 'little')

        return bytes(result)

    def __repr__(self) -> str:
        return (
            f'PVF [{self.uuid.decode(errors="ignore")}]\n'
            f'Ver:{self.pvf_version}\n'
            f'TreeLength:{self.dir_tree_length}\n'
            f'CRC:{hex(self.dir_tree_crc32)}\n'
            f'{self.num_files_in_dir_tree} files'
        )

    def __del__(self):
        if self._fp:
            self._fp.close()


class StringTable:
    """Handles stringtable.bin files containing text data."""

    def __init__(self, table_bytes: bytes, encoding: str = 'big5'):
        self.length = struct.unpack('I', table_bytes[:4])[0]
        self.string_table_str_index = table_bytes[4 : 4 + self.length * 8]
        self.string_table_chunk = table_bytes[4 + self.length * 8 :]
        self.encoding = encoding
        self._converted_cache = {}

        if encoding == 'big5':
            self._preconvert_strings()

    def _preconvert_strings(self):
        """Pre-convert all strings for better performance."""
        for n in range(self.length * 2):
            try:
                str_index = struct.unpack(
                    '<II', self.string_table_str_index[n * 4 : n * 4 + 8]
                )
                value = self.string_table_chunk[str_index[0] : str_index[1]].decode(
                    self.encoding, 'ignore'
                )
                self._converted_cache[n] = convert(value, 'zh-cn')
            except (struct.error, UnicodeDecodeError) as e:
                logger.warning(f'Failed to convert string at index {n}: {e}')
                self._converted_cache[n] = ''

    def __getitem__(self, n: int) -> str:
        """Get string by index."""
        if n in self._converted_cache:
            return self._converted_cache[n]

        try:
            str_index = struct.unpack(
                '<II', self.string_table_str_index[n * 4 : n * 4 + 8]
            )
            value = self.string_table_chunk[str_index[0] : str_index[1]].decode(
                self.encoding, 'ignore'
            )
            result = convert(value, 'zh-cn')
            self._converted_cache[n] = result
            return result
        except (struct.error, UnicodeDecodeError, IndexError) as e:
            logger.warning(f'Failed to get string at index {n}: {e}')
            return ''


class StrFile:
    """Handles *.str files containing text replacements."""

    def __init__(self, content_text: str):
        self.text = convert(content_text, 'zh-cn')
        self.str_dict = {}

        lines = filter(lambda l: '>' in l, self.text.split('\n'))
        for line in lines:
            try:
                key, value = line.split('>', 1)
                self.str_dict[key] = value.replace('\r', '')
            except ValueError:
                continue

    def __getitem__(self, key: str) -> str:
        """Get replacement text by key."""
        return self.str_dict.get(key, 'None')

    def __repr__(self) -> str:
        return f'StrFile object with {len(self.str_dict)} entries'


class LstFile:
    """Handles *.lst files containing ID to path mappings."""

    def __init__(
            self,
            content_bytes: bytes,
            tiny_pvf: 'TinyPVF',
            string_table: StringTable,
            encoding: str = 'big5',
            base_dir: str = '',
    ):
        self.ver_code = content_bytes[:2]
        self.table_list = []
        self.table_dict = {}
        self.str_dict = {}
        self.tiny_pvf = tiny_pvf
        self.string_table = string_table
        self.base_dir = base_dir
        self.encoding = encoding

        self._parse_content(content_bytes)

    def _parse_content(self, content_bytes: bytes):
        """Parse LST file content."""
        i = 2
        while i + 10 <= len(content_bytes):
            try:
                a, aa, b, bb = struct.unpack('<bIbI', content_bytes[i : i + 10])

                if a == 2:
                    index = aa
                elif a == 7:
                    str_index_index = aa
                else:
                    i += 10
                    continue

                if b == 2:
                    index = bb
                elif b == 7:
                    str_index_index = bb
                else:
                    i += 10
                    continue

                string = self.string_table[str_index_index]
                self.table_list.append([index, string])
                self.table_dict[index] = string

            except (struct.error, IndexError) as e:
                logger.warning(f'Failed to parse LST entry at position {i}: {e}')

            i += 10

    def __getitem__(self, n: int) -> str:
        """Get string by index."""
        return self.table_dict.get(n, '')

    def get_str_file(self, n: int) -> StrFile:
        """Get StrFile object for the given index."""
        if n in self.str_dict:
            return self.str_dict[n]

        path = self.table_dict.get(n)
        if not path:
            return StrFile('')

        try:
            content = self.tiny_pvf.read_file_decrypted(path.lower())
            str_file = StrFile(content.decode(self.encoding, 'ignore'))
            self.str_dict[n] = str_file
            return str_file
        except Exception as e:
            logger.warning(f'Failed to load str file for index {n}: {e}')
            return StrFile('')

    def __repr__(self) -> str:
        return f'LstFile object with {len(self.table_list)} entries'


class ContentParser:
    """Utility class for parsing binary content."""

    @staticmethod
    def parse_binary_content(
            content: bytes,
            string_table: StringTable,
            n_string: LstFile,
            string_quote: str = '',
    ) -> Tuple[List[int], List[Any]]:
        """Parse binary content and return types and values."""
        if not content or len(content) < 2:
            return [], []

        shift = 2
        unit_num = (len(content) - 2) // 5

        if unit_num <= 0:
            return [], []

        # Build struct pattern
        struct_pattern = '<'
        unit_types = []

        for i in range(unit_num):
            try:
                unit_type = content[i * 5 + shift]
                unit_types.append(unit_type)

                if unit_type in [2, 3, 5, 6, 7, 8, 9, 10]:
                    struct_pattern += 'Bi'
                elif unit_type == 4:
                    struct_pattern += 'Bf'
                else:
                    struct_pattern += 'Bi'
            except IndexError:
                break

        try:
            units = struct.unpack(struct_pattern, content[2 : 2 + 5 * unit_num])
            types = units[::2]
            values = units[1::2]
        except struct.error as e:
            logger.warning(f'Failed to unpack binary content: {e}')
            return [], []

        # Process values based on types
        values_read = []
        types_in_list = []

        for i in range(min(len(types), len(values))):
            type_val = types[i]
            value = values[i]

            types_in_list.append(type_val)

            try:
                if type_val in [2, 3, 4]:
                    values_read.append(value)
                elif type_val in [5, 6, 8]:
                    values_read.append(string_table[value])
                elif type_val == 7:
                    values_read.append(
                        f'{string_quote}{string_table[value]}{string_quote}'
                    )
                elif type_val == 9:
                    if i + 1 < len(values):
                        str_file = n_string.get_str_file(value)
                        next_value = string_table[values[i + 1]]
                        values_read.append(str_file[next_value])
                    else:
                        values_read.append('')
                else:
                    types_in_list.pop()
            except (IndexError, KeyError) as e:
                logger.warning(f'Failed to process value at index {i}: {e}')
                values_read.append('')

        return types_in_list, values_read

    @staticmethod
    def list_to_dict(
            file_in_list_with_type: Tuple[List[int], List[Any]],
            parent_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convert parsed list to structured dictionary."""
        type_list, file_in_list = file_in_list_with_type

        if not file_in_list:
            return {}

        # Find segment keys with end markers
        segment_keys_with_end_mark = []
        for value in file_in_list:
            if (
                isinstance(value, str)
                and len(value) > 2
                and value[:2] == '[/'
                and value[-1] == ']'
            ):
                segment_keys_with_end_mark.append(value.replace('/', '', 1))

        def add_segment(
                result_dict: Dict[str, Any], segment_key: str, segment_data: Any
        ):
            """Add segment to result dictionary with unique key."""
            if segment_key in result_dict:
                suffix = 1
                while f'{segment_key}-{suffix}' in result_dict:
                    suffix += 1
                segment_key = f'{segment_key}-{suffix}'

            if (
                segment_key in segment_keys_with_end_mark
                and isinstance(segment_data, list)
                and any(
                    isinstance(item, str) and item.startswith('[')
                    for item in segment_data
                )
            ):
                # Recursively process nested segments
                nested_types = [5] * len(segment_data)  # Assume all are segment markers
                result_dict[segment_key] = ContentParser.list_to_dict(
                    (nested_types, segment_data), segment_key
                )
            else:
                result_dict[segment_key] = segment_data

        result = {}
        segment = []
        segment_key = None

        for i, value in enumerate(file_in_list):
            if i < len(type_list) and type_list[i] == 5:  # Segment marker
                if segment_key is None:
                    segment_key = value if '/' not in value else None
                    continue
                else:
                    # Check if this is end of current segment
                    if (
                        segment_key not in segment_keys_with_end_mark
                        or value.replace('/', '') == segment_key
                    ):
                        add_segment(result, segment_key, segment)
                        segment_key = value if '/' not in value else None
                        segment = []
                        continue

            segment.append(value)

        # Add final segment
        if segment_key is not None and segment:
            add_segment(result, segment_key, segment)

        return result

    @staticmethod
    def dict_to_text(
            dict_segment: Dict[str, Any],
            prefix: str = '',
            prefix_add: str = '    ',
            max_seg_num: int = 50,
            depth: int = 4,
    ) -> str:
        """Convert dictionary segment to formatted text."""
        if depth <= 0:
            return f'{prefix}{str(dict_segment)}\n'

        result = ''
        items = list(dict_segment.items())

        if len(items) > max_seg_num:
            items = items[:max_seg_num] + [('...', '')]

        for key, segment in items:
            result += f'{prefix}{key}\n'

            if isinstance(segment, dict):
                result += ContentParser.dict_to_text(
                    segment, prefix + prefix_add, prefix_add, max_seg_num, depth - 1
                )
            else:
                temp_result = ''
                segment_list = segment if isinstance(segment, list) else [segment]

                if len(segment_list) > max_seg_num:
                    segment_list = segment_list[:max_seg_num] + ['...']

                for value in segment_list:
                    temp_result += f'{str(value)} '

                temp_result = temp_result.replace('\n', f'\n{prefix}{prefix_add}')
                temp_result = temp_result.replace('%%', '%')
                result += f'{prefix}{prefix_add}{temp_result}\n'

        return result


class TinyPVF:
    """Main class for PVF file operations."""

    def __init__(self, pvf_header: Optional[PVFHeader] = None, encoding: str = 'big5'):
        self.pvf_structured_dict = {}
        self.file_tree_dict = {}
        self.pvf_header = pvf_header
        self.file_content_dict = {}
        self.string_table: Optional[StringTable] = None
        self.n_string: Optional[LstFile] = None
        self.encoding = encoding

    def load_file_tree(
            self,
            dirs: List[str] = None,
            structured: bool = False,
            pvf_header: Optional[PVFHeader] = None,
    ) -> Dict[str, FileLeaf]:
        """Load file tree from PVF header."""
        if pvf_header is None:
            pvf_header = self.pvf_header

        if pvf_header is None:
            raise ValueError('No PVF header available')

        pvf_header.index = 0
        dirs = dirs or []

        for i in range(pvf_header.num_files_in_dir_tree):
            try:
                # Read file entry data
                fn_bytes = pvf_header.get_header_tree_bytes(4)
                file_path_length_bytes = pvf_header.get_header_tree_bytes(4)
                file_path_length = unpack('I', file_path_length_bytes)[0]
                file_path_bytes = pvf_header.get_header_tree_bytes(file_path_length)
                file_length_bytes = pvf_header.get_header_tree_bytes(4)
                file_crc32_bytes = pvf_header.get_header_tree_bytes(4)
                relative_offset_bytes = pvf_header.get_header_tree_bytes(4)

                # Create file leaf
                file_path = file_path_bytes.decode(errors='replace').lower()
                if file_path.startswith('/'):
                    file_path = file_path[1:]

                leaf = FileLeaf(
                    index=i,
                    fn=unpack('I', fn_bytes)[0],
                    file_path=file_path,
                    file_length=(unpack('I', file_length_bytes)[0] + 3) & 0xFFFFFFFC,
                    file_crc32=unpack('I', file_crc32_bytes)[0],
                    relative_offset=unpack('I', relative_offset_bytes)[0],
                )

                # Filter by directories if specified
                if dirs:
                    leaf_dirs = leaf.file_path.split('/')
                    if not any(d in leaf_dirs for d in dirs):
                        continue

                self.file_tree_dict[leaf.file_path] = leaf

                # Add to structured dict if requested
                if structured:
                    self._add_to_structured_dict(leaf)

            except (struct.error, UnicodeDecodeError) as e:
                logger.warning(f'Failed to parse file entry {i}: {e}')
                continue

        # Initialize string table and n_string if not already done
        if self.string_table is None:
            self._initialize_string_resources()

        return self.file_tree_dict

    def _add_to_structured_dict(self, leaf: FileLeaf):
        """Add file leaf to structured dictionary."""
        path_parts = leaf.file_path.split('/')
        if len(path_parts) <= 1:
            return

        dirs = path_parts[:-1]
        target_dict = self.pvf_structured_dict

        for dir_name in dirs:
            if dir_name not in target_dict:
                target_dict[dir_name] = {}
            target_dict = target_dict[dir_name]

        target_dict[leaf.file_path] = leaf

    def _initialize_string_resources(self):
        """Initialize string table and n_string resources."""
        try:
            stringtable_bytes = self.read_file_decrypted('stringtable.bin')
            self.string_table = StringTable(stringtable_bytes, self.encoding)

            n_string_bytes = self.read_file_decrypted('n_string.lst')
            self.n_string = LstFile(
                n_string_bytes, self, self.string_table, self.encoding
            )
        except Exception as e:
            logger.error(f'Failed to initialize string resources: {e}')
            raise

    def load_lst_file(self, path: str, encoding: str = '') -> LstFile:
        """Load and create LST file object."""
        content = self.read_file_decrypted(path)
        encoding = encoding or self.encoding

        if '/' in path:
            base_dir, _ = path.rsplit('/', 1)
        else:
            base_dir = ''

        return LstFile(content, self, self.string_table, encoding, base_dir)

    def read_file_decrypted(
            self, file_path: str, pvf_header: Optional[PVFHeader] = None
    ) -> bytes:
        """Read and decrypt file content."""
        file_path = file_path.lower().replace('\\', '/')
        if file_path.startswith('/'):
            file_path = file_path[1:]

        # Check cache first
        if file_path in self.file_content_dict:
            return self.file_content_dict[file_path]

        # Get file leaf
        leaf = self.file_tree_dict.get(file_path)
        if leaf is None:
            # Try loading directory
            dir_name = file_path.split('/')[0]
            self.load_file_tree(dirs=[dir_name])
            leaf = self.file_tree_dict.get(file_path)

        if leaf is None:
            raise FileNotFoundError(f'File not found: {file_path}')

        if pvf_header is None:
            pvf_header = self.pvf_header

        try:
            encrypted_data = pvf_header.read_bytes(
                pvf_header.file_pack_index_shift + leaf.relative_offset,
                leaf.file_length,
            )
            result = CryptoUtils.decrypt_bytes_fast(encrypted_data, leaf.file_crc32)
            # Cache the result
            self.file_content_dict[file_path] = result
            return result
        except Exception as e:
            logger.error(f'Failed to decrypt file {file_path}: {e}')
            return b''

    def read_file_as_list(
            self, file_path: str, string_quote: str = ''
    ) -> Tuple[List[int], List[Any]]:
        """Read file and return as parsed list."""
        content = self.read_file_decrypted(file_path)
        return ContentParser.parse_binary_content(
            content, self.string_table, self.n_string, string_quote
        )

    def read_file_as_dict(
            self, file_path: str, string_quote: str = ''
    ) -> Dict[str, Any]:
        """Read file and return as structured dictionary."""
        file_in_list_with_type = self.read_file_as_list(file_path, string_quote)
        return ContentParser.list_to_dict(file_in_list_with_type)

    def read_file_as_text(self, file_path: str, string_quote: str = '') -> str:
        """Read file and return as formatted text."""
        file_dict = self.read_file_as_dict(file_path, string_quote)
        return ContentParser.dict_to_text(file_dict)

    def read_segment_with_key(self, file_path: str, key: str) -> List[Any]:
        """Read specific segment from file by key."""
        type_list, file_in_list = self.read_file_as_list(file_path)

        # Check if this is a multi-segment key (has end marker)
        is_multi_segment_key = any(
            isinstance(value, str) and value == f'[/{key}]' for value in file_in_list
        )

        segment = []
        start = False

        for i, value in enumerate(file_in_list):
            if value == f'[{key}]':
                start = True
            elif (
                start
                and isinstance(value, str)
                and value.startswith('[')
                and value.endswith(']')
            ):
                if is_multi_segment_key and value == f'[/{key}]':
                    break
                elif not is_multi_segment_key:
                    break
                else:
                    segment.append(value)
            elif start:
                segment.append(value)

        return segment


# Utility functions for loading game data
class GameDataLoader:
    """Utility class for loading specific game data types."""

    @staticmethod
    def load_magic_seal_dict(pvf: TinyPVF) -> Dict[int, str]:
        """Load magic seal dictionary."""
        magic_seal_path = 'etc/randomoption/randomizedoptionoverall2.etc'
        logger.info('Loading magic seal data...')

        try:
            type_list, value_list = pvf.read_file_as_list(magic_seal_path)
            postfix_start = False
            magic_seal_dict = {}

            for i in range(len(value_list) - 1):
                if value_list[i] == '[postfix]':
                    postfix_start = True
                elif value_list[i] == '[/postfix]':
                    break
                elif postfix_start and isinstance(value_list[i], int):
                    try:
                        next_value = value_list[i + 1]
                        if isinstance(next_value, str) and '/' not in next_value:
                            clean_value = (
                                next_value.replace('[', '')
                                .replace(']', '')
                                .split(':')[0]
                            )
                            magic_seal_dict[value_list[i]] = convert(
                                clean_value, 'zh-cn'
                            ).strip()
                    except (IndexError, AttributeError):
                        continue

            return magic_seal_dict

        except Exception as e:
            logger.error(f'Failed to load magic seal data: {e}')
            return {0: 'Magic seal data unavailable'}

    @staticmethod
    def load_job_dict(pvf: TinyPVF) -> Tuple[Dict[int, Dict[int, str]], Dict[int, str]]:
        """Load job dictionary and job tag dictionary."""
        logger.info('Loading job information...')
        job_dict = {}
        job_tag_dict = {}

        try:
            characters = pvf.load_lst_file('character/character.lst')

            for id_, path in characters.table_list:
                try:
                    chr_file_dict = pvf.read_file_as_dict(
                        f'{characters.base_dir}/{path}'
                    )

                    # Get grow types
                    grow_types = {}
                    grow_type_names = chr_file_dict.get('[growtype name]', [])
                    for i, name in enumerate(grow_type_names):
                        grow_types[i] = name

                    # Get job tag
                    job_info = chr_file_dict.get('[job]', [])
                    tag = job_info[0] if job_info else ''

                    job_dict[id_] = grow_types
                    job_tag_dict[id_] = tag

                except Exception as e:
                    logger.warning(f'Failed to load job {id_}: {e}')
                    continue

        except Exception as e:
            logger.error(f'Failed to load job data: {e}')

        return job_dict, job_tag_dict

    @staticmethod
    def load_exp_table(pvf: TinyPVF) -> List[int]:
        """Load experience table."""
        try:
            exp_table_path = 'character/exptable.tbl'
            _, exp_table_list = pvf.read_file_as_list(exp_table_path)
            return [value for value in exp_table_list if isinstance(value, int)]
        except Exception as e:
            logger.error(f'Failed to load experience table: {e}')
            return []


def merge_dicts_recursive(
        dict1: Dict[str, Any], dict2: Dict[str, Any]
) -> Dict[str, Any]:
    """Recursively merge two dictionaries."""
    for key, value in dict2.items():
        if key not in dict1:
            dict1[key] = value
        elif isinstance(value, dict) and isinstance(dict1[key], dict):
            merge_dicts_recursive(dict1[key], value)
        else:
            dict1[key] = value
    return dict1


# Main function for loading all item data
def load_all_item_data(pvf: TinyPVF, generate_keywords: bool = False) -> Dict[str, Any]:
    """Load all item data from PVF file."""
    logger.info('Loading PVF file tree...')
    pvf.load_file_tree(
        ['stackable', 'character', 'etc', 'equipment', 'dungeon', 'n_quest']
    )

    all_item_dict = {}

    # Load magic seal data
    all_item_dict['magicSealDict'] = GameDataLoader.load_magic_seal_dict(pvf)

    # Load job data
    job_dict, job_tag_dict = GameDataLoader.load_job_dict(pvf)
    all_item_dict['jobDict'] = job_dict
    all_item_dict['jobTagDict'] = job_tag_dict

    # Load experience table
    all_item_dict['expTable'] = GameDataLoader.load_exp_table(pvf)

    logger.info('All item data loaded successfully')
    return all_item_dict
