"""
Unit tests for the optimized PVF Reader module.

This test suite covers all major functionality of the optimized pvfReader module,
including file parsing, decryption, content conversion, and data loading.
"""

import unittest
import tempfile
import struct
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import logging

# Import the optimized modules
import sys

sys.path.append("../dnfpkgtool")

from dnfpkgtool.pvfReader_optimized import (
    PVFHeader,
    StringTable,
    StrFile,
    LstFile,
    TinyPVF,
    CryptoUtils,
    ContentParser,
    GameDataLoader,
    FileLeaf,
    load_all_item_data,
    merge_dicts_recursive,
)


class TestCryptoUtils(unittest.TestCase):
    """Test cases for CryptoUtils class."""

    def test_decrypt_bytes_empty_input(self):
        """Test decryption with empty input."""
        result = CryptoUtils.decrypt_bytes(b"", 0x12345678)
        self.assertEqual(result, b"")

    def test_decrypt_bytes_small_input(self):
        """Test decryption with input smaller than 4 bytes."""
        result = CryptoUtils.decrypt_bytes(b"abc", 0x12345678)
        self.assertEqual(result, b"abc")

    def test_decrypt_bytes_normal_input(self):
        """Test decryption with normal 4-byte aligned input."""
        # Create test data (8 bytes = 2 * 4-byte chunks)
        test_data = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        crc = 0x12345678

        result = CryptoUtils.decrypt_bytes(test_data, crc)
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 8)

    @patch("dnfpkgtool.pvfReader_optimized.HAS_DLL", False)
    def test_decrypt_bytes_fast_fallback(self):
        """Test that fast decryption falls back to normal when DLL unavailable."""
        test_data = b"\x01\x02\x03\x04"
        crc = 0x12345678

        result = CryptoUtils.decrypt_bytes_fast(test_data, crc)
        expected = CryptoUtils.decrypt_bytes(test_data, crc)
        self.assertEqual(result, expected)


class TestFileLeaf(unittest.TestCase):
    """Test cases for FileLeaf dataclass."""

    def test_file_leaf_creation(self):
        """Test FileLeaf creation with all fields."""
        leaf = FileLeaf(
            index=1,
            fn=123,
            file_path="test/path.txt",
            file_length=1024,
            file_crc32=0x12345678,
            relative_offset=2048,
        )

        self.assertEqual(leaf.index, 1)
        self.assertEqual(leaf.fn, 123)
        self.assertEqual(leaf.file_path, "test/path.txt")
        self.assertEqual(leaf.file_length, 1024)
        self.assertEqual(leaf.file_crc32, 0x12345678)
        self.assertEqual(leaf.relative_offset, 2048)
        self.assertEqual(leaf.content, b"")


class TestStringTable(unittest.TestCase):
    """Test cases for StringTable class."""

    def setUp(self):
        """Set up test data for StringTable tests."""
        # Create mock string table data
        # Format: [length:4][index_data][string_data]
        self.length = 2
        self.string_data = b"Hello\x00World\x00"

        # Create index data: 2 strings, each with start and end positions
        index_data = struct.pack("<IIII", 0, 6, 6, 12)  # "Hello\x00", "World\x00"

        self.table_bytes = (
            struct.pack("I", self.length)  # Length
            + index_data  # Index data (2 strings * 2 positions * 4 bytes)
            + self.string_data  # String data
        )

    def test_string_table_creation(self):
        """Test StringTable creation and basic functionality."""
        table = StringTable(self.table_bytes, encoding="utf-8")
        self.assertEqual(table.length, self.length)
        self.assertEqual(table.encoding, "utf-8")

    def test_string_table_getitem(self):
        """Test string retrieval by index."""
        table = StringTable(self.table_bytes, encoding="utf-8")

        # Note: StringTable expects index pairs, so we test with even indices
        result0 = table[0]  # Should get first string
        result1 = table[2]  # Should get second string

        self.assertIsInstance(result0, str)
        self.assertIsInstance(result1, str)

    def test_string_table_invalid_index(self):
        """Test string retrieval with invalid index."""
        table = StringTable(self.table_bytes, encoding="utf-8")

        # Should return empty string for invalid index
        result = table[999]
        self.assertEqual(result, "")

    def test_string_table_malformed_data(self):
        """Test StringTable with malformed data."""
        malformed_data = b"\x01\x00\x00\x00"  # Length=1 but no index/string data

        table = StringTable(malformed_data, encoding="utf-8")
        result = table[0]
        self.assertEqual(result, "")


class TestStrFile(unittest.TestCase):
    """Test cases for StrFile class."""

    def test_str_file_creation(self):
        """Test StrFile creation and parsing."""
        content = "key1>value1\nkey2>value2\r\nkey3>value3 with spaces\n"
        str_file = StrFile(content)

        self.assertEqual(str_file["key1"], "value1")
        self.assertEqual(str_file["key2"], "value2")
        self.assertEqual(str_file["key3"], "value3 with spaces")

    def test_str_file_missing_key(self):
        """Test StrFile with missing key."""
        content = "key1>value1\n"
        str_file = StrFile(content)

        self.assertEqual(str_file["nonexistent"], "None")

    def test_str_file_malformed_lines(self):
        """Test StrFile with malformed lines."""
        content = "key1>value1\nmalformed_line\nkey2>value2\n"
        str_file = StrFile(content)

        self.assertEqual(str_file["key1"], "value1")
        self.assertEqual(str_file["key2"], "value2")
        self.assertEqual(str_file["malformed_line"], "None")

    def test_str_file_carriage_return_removal(self):
        """Test that carriage returns are properly removed."""
        content = "key1>value1\r\n"
        str_file = StrFile(content)

        self.assertEqual(str_file["key1"], "value1")  # \r should be removed


class TestLstFile(unittest.TestCase):
    """Test cases for LstFile class."""

    def setUp(self):
        """Set up test data for LstFile tests."""
        self.mock_tiny_pvf = Mock()
        self.mock_string_table = Mock()
        self.mock_string_table.__getitem__ = Mock(side_effect=lambda x: f"string_{x}")

        # Create mock LST file content
        # Format: [version:2][entries...]
        # Each entry: [type1:1][value1:4][type2:1][value2:4]
        self.lst_content = (
            b"\x01\x00"  # Version
            + struct.pack("<bIbI", 2, 123, 7, 0)  # Entry 1: index=123, string_index=0
            + struct.pack("<bIbI", 2, 456, 7, 1)  # Entry 2: index=456, string_index=1
        )

    def test_lst_file_creation(self):
        """Test LstFile creation and parsing."""
        lst_file = LstFile(
            self.lst_content,
            self.mock_tiny_pvf,
            self.mock_string_table,
            encoding="utf-8",
        )

        self.assertEqual(len(lst_file.table_list), 2)
        self.assertEqual(lst_file.table_dict[123], "string_0")
        self.assertEqual(lst_file.table_dict[456], "string_1")

    def test_lst_file_getitem(self):
        """Test LstFile item retrieval."""
        lst_file = LstFile(
            self.lst_content,
            self.mock_tiny_pvf,
            self.mock_string_table,
            encoding="utf-8",
        )

        self.assertEqual(lst_file[123], "string_0")
        self.assertEqual(lst_file[456], "string_1")
        self.assertEqual(lst_file[999], "")  # Non-existent key

    def test_lst_file_get_str_file(self):
        """Test StrFile retrieval from LstFile."""
        self.mock_tiny_pvf.read_file_decrypted.return_value = b"key1>value1\n"

        lst_file = LstFile(
            self.lst_content,
            self.mock_tiny_pvf,
            self.mock_string_table,
            encoding="utf-8",
        )

        str_file = lst_file.get_str_file(123)
        self.assertIsInstance(str_file, StrFile)
        self.assertEqual(str_file["key1"], "value1")

    def test_lst_file_malformed_content(self):
        """Test LstFile with malformed content."""
        malformed_content = b"\x01\x00\x01\x02"  # Too short

        lst_file = LstFile(
            malformed_content,
            self.mock_tiny_pvf,
            self.mock_string_table,
            encoding="utf-8",
        )

        self.assertEqual(len(lst_file.table_list), 0)


class TestContentParser(unittest.TestCase):
    """Test cases for ContentParser class."""

    def setUp(self):
        """Set up test data for ContentParser tests."""
        self.mock_string_table = Mock()
        self.mock_string_table.__getitem__ = Mock(side_effect=lambda x: f"string_{x}")

        self.mock_n_string = Mock()
        self.mock_str_file = Mock()
        self.mock_str_file.__getitem__ = Mock(return_value="str_value")
        self.mock_n_string.get_str_file.return_value = self.mock_str_file

    def test_parse_binary_content_empty(self):
        """Test parsing empty binary content."""
        result = ContentParser.parse_binary_content(
            b"", self.mock_string_table, self.mock_n_string
        )
        self.assertEqual(result, ([], []))

    def test_parse_binary_content_too_small(self):
        """Test parsing binary content that's too small."""
        result = ContentParser.parse_binary_content(
            b"\x01", self.mock_string_table, self.mock_n_string
        )
        self.assertEqual(result, ([], []))

    def test_parse_binary_content_normal(self):
        """Test parsing normal binary content."""
        # Create test content: version(2) + 1 unit(5 bytes)
        # Unit: type=2(int), value=123
        content = b"\x01\x00" + struct.pack("<Bi", 2, 123)

        types, values = ContentParser.parse_binary_content(
            content, self.mock_string_table, self.mock_n_string
        )

        self.assertEqual(len(types), 1)
        self.assertEqual(len(values), 1)
        self.assertEqual(types[0], 2)
        self.assertEqual(values[0], 123)

    def test_parse_binary_content_string_type(self):
        """Test parsing binary content with string type."""
        # Create test content with string type (5)
        content = b"\x01\x00" + struct.pack("<Bi", 5, 42)

        types, values = ContentParser.parse_binary_content(
            content, self.mock_string_table, self.mock_n_string
        )

        self.assertEqual(len(types), 1)
        self.assertEqual(len(values), 1)
        self.assertEqual(types[0], 5)
        self.assertEqual(values[0], "string_42")

    def test_list_to_dict_empty(self):
        """Test converting empty list to dict."""
        result = ContentParser.list_to_dict(([], []))
        self.assertEqual(result, {})

    def test_list_to_dict_simple(self):
        """Test converting simple list to dict."""
        types = [5, 2, 5, 2]  # segment, value, segment, value
        values = ["[segment1]", 123, "[segment2]", 456]

        result = ContentParser.list_to_dict((types, values))

        self.assertIn("[segment1]", result)
        self.assertIn("[segment2]", result)
        self.assertEqual(result["[segment1]"], [123])
        self.assertEqual(result["[segment2]"], [456])

    def test_dict_to_text_empty(self):
        """Test converting empty dict to text."""
        result = ContentParser.dict_to_text({})
        self.assertEqual(result, "")

    def test_dict_to_text_simple(self):
        """Test converting simple dict to text."""
        test_dict = {"key1": ["value1", "value2"], "key2": {"nested": ["nested_value"]}}

        result = ContentParser.dict_to_text(test_dict)

        self.assertIn("key1", result)
        self.assertIn("key2", result)
        self.assertIn("value1", result)
        self.assertIn("nested", result)


class TestPVFHeader(unittest.TestCase):
    """Test cases for PVFHeader class."""

    def setUp(self):
        """Set up test PVF header data."""
        # Create minimal valid PVF header
        self.uuid = b"test_uuid_12345678901234567890123456"
        self.header_data = (
            struct.pack("i", len(self.uuid))  # UUID length
            + self.uuid  # UUID
            + struct.pack("i", 1)  # PVF version
            + struct.pack("i", 8)  # Dir tree length
            + struct.pack("I", 0x12345678)  # Dir tree CRC32
            + struct.pack("I", 0)  # Number of files
            + b"\x00" * 8  # Dummy tree data
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_pvf_header_creation(self, mock_file):
        """Test PVFHeader creation."""
        # Create a proper sequence of reads that matches the header structure
        reads = []
        pos = 0

        # UUID length
        reads.append(self.header_data[pos : pos + 4])
        pos += 4

        # UUID
        uuid_len = len(self.uuid)
        reads.append(self.header_data[pos : pos + uuid_len])
        pos += uuid_len

        # Rest of header fields
        while pos < len(self.header_data):
            reads.append(self.header_data[pos : pos + 4])
            pos += 4

        # Tree data
        reads.append(b"\x00" * 8)

        mock_file.return_value.read.side_effect = reads
        mock_file.return_value.tell.return_value = len(self.header_data) - 8

        with patch.object(CryptoUtils, "decrypt_bytes_fast", return_value=b"\x00" * 8):
            header = PVFHeader("test.pvf")

            self.assertEqual(header.uuid, self.uuid)
            self.assertEqual(header.pvf_version, 1)
            self.assertEqual(header.dir_tree_length, 8)
            self.assertEqual(header.dir_tree_crc32, 0x12345678)
            self.assertEqual(header.num_files_in_dir_tree, 0)

    def test_pvf_header_repr(self):
        """Test PVFHeader string representation."""
        with patch("builtins.open", new_callable=mock_open):
            with patch.object(PVFHeader, "_read_header"):
                header = PVFHeader("test.pvf")
                header.uuid = self.uuid
                header.pvf_version = 1
                header.dir_tree_length = 8
                header.dir_tree_crc32 = 0x12345678
                header.num_files_in_dir_tree = 0

                repr_str = repr(header)
                self.assertIn("test_uuid", repr_str)
                self.assertIn("Ver:1", repr_str)


class TestTinyPVF(unittest.TestCase):
    """Test cases for TinyPVF class."""

    def setUp(self):
        """Set up test TinyPVF instance."""
        self.mock_header = Mock()
        self.mock_header.num_files_in_dir_tree = 1
        self.mock_header.index = 0

        # Mock file entry data
        self.mock_header.get_header_tree_bytes.side_effect = [
            struct.pack("I", 1),  # fn
            struct.pack("I", 8),  # path length
            b"test.txt",  # path
            struct.pack("I", 100),  # file length
            struct.pack("I", 0x12345678),  # CRC32
            struct.pack("I", 0),  # relative offset
        ]

        self.tiny_pvf = TinyPVF(self.mock_header)

    def test_tiny_pvf_creation(self):
        """Test TinyPVF creation."""
        self.assertEqual(self.tiny_pvf.pvf_header, self.mock_header)
        self.assertEqual(self.tiny_pvf.encoding, "big5")
        self.assertEqual(len(self.tiny_pvf.file_tree_dict), 0)

    @patch.object(TinyPVF, "_initialize_string_resources")
    def test_load_file_tree(self, mock_init_strings):
        """Test loading file tree."""
        mock_init_strings.return_value = None

        result = self.tiny_pvf.load_file_tree()

        self.assertEqual(len(result), 1)
        self.assertIn("test.txt", result)

        leaf = result["test.txt"]
        self.assertIsInstance(leaf, FileLeaf)
        self.assertEqual(leaf.file_path, "test.txt")

    def test_read_file_decrypted_cached(self):
        """Test reading cached file content."""
        self.tiny_pvf.file_content_dict["test.txt"] = b"cached_content"

        result = self.tiny_pvf.read_file_decrypted("test.txt")
        self.assertEqual(result, b"cached_content")

    def test_read_file_decrypted_not_found(self):
        """Test reading non-existent file."""
        # Mock the header to avoid infinite recursion
        self.mock_header.get_header_tree_bytes.side_effect = []
        self.mock_header.num_files_in_dir_tree = 0

        with self.assertRaises(FileNotFoundError):
            self.tiny_pvf.read_file_decrypted("nonexistent.txt")

    @patch.object(ContentParser, "parse_binary_content")
    def test_read_file_as_list(self, mock_parse):
        """Test reading file as list."""
        mock_parse.return_value = ([2], [123])
        self.tiny_pvf.file_content_dict["test.txt"] = b"test_content"

        result = self.tiny_pvf.read_file_as_list("test.txt")

        self.assertEqual(result, ([2], [123]))
        mock_parse.assert_called_once()

    @patch.object(ContentParser, "list_to_dict")
    @patch.object(TinyPVF, "read_file_as_list")
    def test_read_file_as_dict(self, mock_read_list, mock_list_to_dict):
        """Test reading file as dictionary."""
        mock_read_list.return_value = ([2], [123])
        mock_list_to_dict.return_value = {"key": "value"}

        result = self.tiny_pvf.read_file_as_dict("test.txt")

        self.assertEqual(result, {"key": "value"})
        mock_read_list.assert_called_once_with("test.txt", "")
        mock_list_to_dict.assert_called_once_with(([2], [123]))


class TestGameDataLoader(unittest.TestCase):
    """Test cases for GameDataLoader class."""

    def setUp(self):
        """Set up test GameDataLoader."""
        self.mock_pvf = Mock()

    def test_load_magic_seal_dict_success(self):
        """Test successful magic seal dictionary loading."""
        # Mock PVF response
        self.mock_pvf.read_file_as_list.return_value = (
            [5, 5, 2, 7, 5],
            ["[postfix]", "[magic_seal_1]", 123, "Magic Seal Name", "[/postfix]"],
        )

        result = GameDataLoader.load_magic_seal_dict(self.mock_pvf)

        self.assertIsInstance(result, dict)
        self.assertIn(123, result)

    def test_load_magic_seal_dict_failure(self):
        """Test magic seal dictionary loading failure."""
        self.mock_pvf.read_file_as_list.side_effect = Exception("File not found")

        result = GameDataLoader.load_magic_seal_dict(self.mock_pvf)

        self.assertIn(0, result)
        self.assertIn("unavailable", result[0])

    def test_load_job_dict_success(self):
        """Test successful job dictionary loading."""
        # Mock LST file
        mock_lst = Mock()
        mock_lst.table_list = [(1, "job1.chr"), (2, "job2.chr")]
        mock_lst.base_dir = "character"

        self.mock_pvf.load_lst_file.return_value = mock_lst
        self.mock_pvf.read_file_as_dict.side_effect = [
            {"[growtype name]": ["Fighter", "Gunner"], "[job]": ["fighter"]},
            {"[growtype name]": ["Mage", "Priest"], "[job]": ["mage"]},
        ]

        job_dict, job_tag_dict = GameDataLoader.load_job_dict(self.mock_pvf)

        self.assertEqual(len(job_dict), 2)
        self.assertEqual(len(job_tag_dict), 2)
        self.assertEqual(job_dict[1][0], "Fighter")
        self.assertEqual(job_tag_dict[1], "fighter")

    def test_load_exp_table_success(self):
        """Test successful experience table loading."""
        self.mock_pvf.read_file_as_list.return_value = (
            [2, 2, 2, 7],
            [100, 200, 300, "text"],
        )

        result = GameDataLoader.load_exp_table(self.mock_pvf)

        self.assertEqual(result, [100, 200, 300])

    def test_load_exp_table_failure(self):
        """Test experience table loading failure."""
        self.mock_pvf.read_file_as_list.side_effect = Exception("File error")

        result = GameDataLoader.load_exp_table(self.mock_pvf)

        self.assertEqual(result, [])


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_merge_dicts_recursive_simple(self):
        """Test simple dictionary merging."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}

        result = merge_dicts_recursive(dict1, dict2)

        expected = {"a": 1, "b": 2, "c": 3, "d": 4}
        self.assertEqual(result, expected)

    def test_merge_dicts_recursive_nested(self):
        """Test nested dictionary merging."""
        dict1 = {"a": {"x": 1, "y": 2}, "b": 3}
        dict2 = {"a": {"y": 20, "z": 30}, "c": 4}

        result = merge_dicts_recursive(dict1, dict2)

        expected = {"a": {"x": 1, "y": 20, "z": 30}, "b": 3, "c": 4}
        self.assertEqual(result, expected)

    def test_merge_dicts_recursive_overwrite(self):
        """Test dictionary merging with value overwriting."""
        dict1 = {"a": 1, "b": {"x": 10}}
        dict2 = {"a": 2, "b": "string"}

        result = merge_dicts_recursive(dict1, dict2)

        expected = {"a": 2, "b": "string"}
        self.assertEqual(result, expected)

    @patch.object(GameDataLoader, "load_magic_seal_dict")
    @patch.object(GameDataLoader, "load_job_dict")
    @patch.object(GameDataLoader, "load_exp_table")
    def test_load_all_item_data(self, mock_exp, mock_job, mock_magic):
        """Test loading all item data."""
        mock_pvf = Mock()
        mock_pvf.load_file_tree.return_value = {}

        mock_magic.return_value = {1: "magic"}
        mock_job.return_value = ({1: {0: "job"}}, {1: "tag"})
        mock_exp.return_value = [100, 200]

        result = load_all_item_data(mock_pvf)

        self.assertIn("magicSealDict", result)
        self.assertIn("jobDict", result)
        self.assertIn("jobTagDict", result)
        self.assertIn("expTable", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        """Set up integration test environment."""
        # Create a temporary PVF-like file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

        # Write minimal PVF header
        uuid = b"test_uuid_123456789012345678901234"
        header_data = (
            struct.pack("i", len(uuid))  # UUID length
            + uuid  # UUID
            + struct.pack("i", 1)  # PVF version
            + struct.pack("i", 8)  # Dir tree length
            + struct.pack("I", 0x12345678)  # Dir tree CRC32
            + struct.pack("I", 0)  # Number of files
            + b"\x00" * 8  # Dummy tree data
        )

        self.temp_file.write(header_data)
        self.temp_file.close()

    def tearDown(self):
        """Clean up integration test environment."""
        Path(self.temp_file.name).unlink(missing_ok=True)

    @patch.object(CryptoUtils, "decrypt_bytes_fast")
    def test_full_workflow_header_only(self, mock_decrypt):
        """Test complete workflow with header-only PVF file."""
        mock_decrypt.return_value = b"\x00" * 8

        # Test header loading
        header = PVFHeader(self.temp_file.name)
        self.assertIsNotNone(header)

        # Test TinyPVF creation
        tiny_pvf = TinyPVF(header)
        self.assertEqual(tiny_pvf.pvf_header, header)

        # Test file tree loading (should work with 0 files)
        with patch.object(tiny_pvf, "_initialize_string_resources"):
            file_tree = tiny_pvf.load_file_tree()
            self.assertEqual(len(file_tree), 0)


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)

    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
