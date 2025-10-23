"""
Test data generator for PVF Reader tests.

This module provides utilities to generate mock PVF data for testing purposes.
"""

import random
import struct
from typing import Any, Dict, List, Tuple


class MockPVFDataGenerator:
    """Generator for mock PVF file data."""

    @staticmethod
    def generate_pvf_header(num_files: int = 5, uuid: bytes = None) -> bytes:
        """Generate a mock PVF header."""
        if uuid is None:
            uuid = b'mock_test_uuid_1234567890123456'

        # Calculate tree length (simplified)
        tree_length = num_files * 32  # Approximate size per file entry

        header_data = (
            struct.pack('i', len(uuid))  # UUID length
            + uuid  # UUID
            + struct.pack('i', 1)  # PVF version
            + struct.pack('i', tree_length)  # Dir tree length
            + struct.pack('I', 0x12345678)  # Dir tree CRC32
            + struct.pack('I', num_files)  # Number of files
        )

        return header_data

    @staticmethod
    def generate_file_tree_entry(
            file_path: str, file_size: int = 1024, offset: int = 0
    ) -> bytes:
        """Generate a mock file tree entry."""
        path_bytes = file_path.encode('utf-8')

        entry_data = (
            struct.pack('I', random.randint(1, 1000))  # fn
            + struct.pack('I', len(path_bytes))  # path length
            + path_bytes  # path
            + struct.pack('I', file_size)  # file length
            + struct.pack('I', random.randint(0x10000000, 0xFFFFFFFF))  # CRC32
            + struct.pack('I', offset)  # relative offset
        )

        return entry_data

    @staticmethod
    def generate_string_table(strings: List[str]) -> bytes:
        """Generate a mock string table."""
        string_data = b''
        index_data = b''
        offset = 0

        for string in strings:
            string_bytes = string.encode('utf-8') + b'\x00'
            string_data += string_bytes

            # Add index entry (start, end)
            index_data += struct.pack('<II', offset, offset + len(string_bytes))
            offset += len(string_bytes)

        # Create complete table
        table_bytes = struct.pack('I', len(strings)) + index_data + string_data

        return table_bytes

    @staticmethod
    def generate_lst_file(entries: List[Tuple[int, int]]) -> bytes:
        """Generate a mock LST file."""
        content = b'\x01\x00'  # Version

        for item_id, string_index in entries:
            # Add entry: type=2, value=item_id, type=7, value=string_index
            content += struct.pack('<bIbI', 2, item_id, 7, string_index)

        return content

    @staticmethod
    def generate_binary_content(entries: List[Tuple[int, Any]]) -> bytes:
        """Generate mock binary content with various data types."""
        content = b'\x01\x00'  # Version

        for data_type, value in entries:
            if data_type in [2, 3]:  # Integer types
                content += struct.pack('<Bi', data_type, int(value))
            elif data_type == 4:  # Float type
                content += struct.pack('<Bf', data_type, float(value))
            elif data_type in [5, 6, 7, 8]:  # String types
                content += struct.pack('<Bi', data_type, int(value))
            else:
                content += struct.pack('<Bi', data_type, int(value))

        return content

    @staticmethod
    def generate_str_file_content(mappings: Dict[str, str]) -> str:
        """Generate mock STR file content."""
        lines = []
        for key, value in mappings.items():
            lines.append(f'{key}>{value}')

        return '\n'.join(lines) + '\n'


class MockGameData:
    """Mock game data for testing."""

    @staticmethod
    def get_sample_items() -> List[Dict[str, Any]]:
        """Get sample item data."""
        return [
            {
                'id': 1001,
                'name': 'Iron Sword',
                'type': 'weapon',
                'level': 10,
                'stats': {'attack': 50, 'durability': 100},
            },
            {
                'id': 1002,
                'name': 'Health Potion',
                'type': 'consumable',
                'level': 1,
                'stats': {'heal': 100},
            },
            {
                'id': 1003,
                'name': 'Magic Ring',
                'type': 'accessory',
                'level': 15,
                'stats': {'magic': 25, 'mana': 50},
            },
        ]

    @staticmethod
    def get_sample_jobs() -> List[Dict[str, Any]]:
        """Get sample job data."""
        return [
            {
                'id': 1,
                'name': 'Fighter',
                'grow_types': {0: 'Male Fighter', 1: 'Female Fighter'},
                'tag': 'fighter',
            },
            {
                'id': 2,
                'name': 'Mage',
                'grow_types': {0: 'Male Mage', 1: 'Female Mage'},
                'tag': 'mage',
            },
            {
                'id': 3,
                'name': 'Gunner',
                'grow_types': {0: 'Male Gunner', 1: 'Female Gunner'},
                'tag': 'gunner',
            },
        ]

    @staticmethod
    def get_sample_magic_seals() -> Dict[int, str]:
        """Get sample magic seal data."""
        return {
            1: 'Strength Enhancement',
            2: 'Intelligence Boost',
            3: 'Vitality Increase',
            4: 'Spirit Enhancement',
            5: 'Critical Hit Rate',
            6: 'Attack Speed',
            7: 'Movement Speed',
            8: 'Magic Defense',
        }

    @staticmethod
    def get_sample_exp_table() -> List[int]:
        """Get sample experience table."""
        exp_table = []
        base_exp = 100

        for level in range(1, 101):  # Levels 1-100
            exp_table.append(base_exp)
            base_exp = int(base_exp * 1.1)  # 10% increase per level

        return exp_table


def create_test_pvf_file(file_path: str, num_files: int = 5) -> None:
    """Create a complete test PVF file."""
    generator = MockPVFDataGenerator()

    # Generate header
    header = generator.generate_pvf_header(num_files)

    # Generate file tree entries
    file_entries = []
    file_paths = [
        'stringtable.bin',
        'n_string.lst',
        'stackable/item1.stk',
        'equipment/sword1.equ',
        'character/fighter.chr',
    ]

    tree_data = b''
    for i, path in enumerate(file_paths[:num_files]):
        entry = generator.generate_file_tree_entry(path, 1024, i * 1024)
        tree_data += entry

    # Pad tree data to match header length
    tree_length = struct.unpack('i', header[len(header) - 20 : len(header) - 16])[0]
    if len(tree_data) < tree_length:
        tree_data += b'\x00' * (tree_length - len(tree_data))

    # Generate file data
    file_data = b''
    for i in range(num_files):
        # Generate 1KB of dummy file data
        dummy_data = b'\x00' * 1024
        file_data += dummy_data

    # Write complete PVF file
    with open(file_path, 'wb') as f:
        f.write(header)
        f.write(tree_data)
        f.write(file_data)


if __name__ == '__main__':
    # Example usage
    generator = MockPVFDataGenerator()

    # Generate sample string table
    strings = ['Hello', 'World', 'Test', 'String', 'Table']
    string_table = generator.generate_string_table(strings)
    print(f'Generated string table: {len(string_table)} bytes')

    # Generate sample LST file
    lst_entries = [(1001, 0), (1002, 1), (1003, 2)]
    lst_file = generator.generate_lst_file(lst_entries)
    print(f'Generated LST file: {len(lst_file)} bytes')

    # Generate sample binary content
    binary_entries = [(2, 123), (5, 0), (2, 456), (5, 1)]
    binary_content = generator.generate_binary_content(binary_entries)
    print(f'Generated binary content: {len(binary_content)} bytes')

    # Create a test PVF file
    create_test_pvf_file('test_sample.pvf', 3)
    print('Created test PVF file: test_sample.pvf')
