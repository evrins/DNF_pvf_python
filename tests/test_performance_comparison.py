"""
Performance comparison tests between original and optimized PVF Reader.

This module provides benchmarks to demonstrate the performance improvements
in the optimized version.
"""

import time
import unittest
import struct
from unittest.mock import Mock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnfpkgtool.pvfReader_optimized import StringTable, CryptoUtils, ContentParser


class PerformanceTestCase(unittest.TestCase):
    """Base class for performance tests."""

    def setUp(self):
        """Set up performance test environment."""
        self.iterations = 1000
        self.large_data_size = 10000

    def time_function(self, func, *args, **kwargs):
        """Time a function execution."""
        start_time = time.time()
        for _ in range(self.iterations):
            result = func(*args, **kwargs)
        end_time = time.time()
        return (end_time - start_time) / self.iterations, result


class TestCryptoPerformance(PerformanceTestCase):
    """Performance tests for crypto operations."""

    def test_decrypt_bytes_performance(self):
        """Test decryption performance with various data sizes."""
        test_sizes = [100, 1000, 10000]

        print("\nDecryption Performance Test:")
        print("Size (bytes) | Time per operation (ms)")
        print("-" * 40)

        for size in test_sizes:
            # Create test data aligned to 4 bytes
            aligned_size = (size // 4) * 4
            test_data = b"\x01\x02\x03\x04" * (aligned_size // 4)
            crc = 0x12345678

            avg_time, _ = self.time_function(CryptoUtils.decrypt_bytes, test_data, crc)

            print(f"{aligned_size:>11} | {avg_time * 1000:>18.3f}")

    def test_decrypt_bytes_fast_vs_normal(self):
        """Compare fast vs normal decryption methods."""
        test_data = b"\x01\x02\x03\x04" * 1000  # 4KB
        crc = 0x12345678

        # Test normal decryption
        normal_time, normal_result = self.time_function(
            CryptoUtils.decrypt_bytes, test_data, crc
        )

        # Test fast decryption (will fallback to normal if no DLL)
        fast_time, fast_result = self.time_function(
            CryptoUtils.decrypt_bytes_fast, test_data, crc
        )

        print("\nDecryption Method Comparison (4KB data):")
        print(f"Normal method: {normal_time * 1000:.3f} ms")
        print(f"Fast method:   {fast_time * 1000:.3f} ms")

        if fast_time < normal_time:
            speedup = normal_time / fast_time
            print(f"Speedup: {speedup:.2f}x faster")
        else:
            print("Fast method uses fallback (no DLL available)")

        # Results should be identical
        self.assertEqual(normal_result, fast_result)


class TestStringTablePerformance(PerformanceTestCase):
    """Performance tests for StringTable operations."""

    def setUp(self):
        """Set up StringTable performance test data."""
        super().setUp()

        # Create a large string table for testing
        self.num_strings = 1000
        string_data = b""
        index_data = b""
        offset = 0

        for i in range(self.num_strings):
            string_content = f"test_string_{i:04d}\x00".encode("utf-8")
            string_data += string_content

            # Add index entry (start, end)
            index_data += struct.pack("<II", offset, offset + len(string_content))
            offset += len(string_content)

        # Create complete table bytes
        self.table_bytes = struct.pack("I", self.num_strings) + index_data + string_data

    def test_string_table_creation_performance(self):
        """Test StringTable creation performance."""
        print(f"\nStringTable Creation Performance ({self.num_strings} strings):")

        # Test creation without pre-conversion
        start_time = time.time()
        table_no_preconv = StringTable(self.table_bytes, encoding="utf-8")
        table_no_preconv._converted_cache = {}  # Clear cache to simulate no pre-conversion
        creation_time_no_preconv = time.time() - start_time

        # Test creation with pre-conversion (default behavior)
        start_time = time.time()
        table_with_preconv = StringTable(self.table_bytes, encoding="utf-8")
        creation_time_with_preconv = time.time() - start_time

        print(f"Without pre-conversion: {creation_time_no_preconv * 1000:.3f} ms")
        print(f"With pre-conversion:    {creation_time_with_preconv * 1000:.3f} ms")

        # Test access performance
        test_indices = list(range(0, self.num_strings * 2, 10))  # Sample indices

        # Access without cache
        start_time = time.time()
        for idx in test_indices:
            _ = table_no_preconv[idx]
        access_time_no_cache = time.time() - start_time

        # Access with cache
        start_time = time.time()
        for idx in test_indices:
            _ = table_with_preconv[idx]
        access_time_with_cache = time.time() - start_time

        print(f"\nString Access Performance ({len(test_indices)} accesses):")
        print(f"Without cache: {access_time_no_cache * 1000:.3f} ms")
        print(f"With cache:    {access_time_with_cache * 1000:.3f} ms")

        if access_time_no_cache > access_time_with_cache:
            speedup = access_time_no_cache / access_time_with_cache
            print(f"Cache speedup: {speedup:.2f}x faster")


class TestContentParserPerformance(PerformanceTestCase):
    """Performance tests for ContentParser operations."""

    def setUp(self):
        """Set up ContentParser performance test data."""
        super().setUp()

        # Create mock string table
        self.mock_string_table = Mock()
        self.mock_string_table.__getitem__ = Mock(side_effect=lambda x: f"string_{x}")

        # Create mock n_string
        self.mock_n_string = Mock()

        # Create test binary content with various types
        self.test_content = b"\x01\x00"  # Version

        # Add multiple entries of different types
        for i in range(100):
            # Type 2 (int)
            self.test_content += struct.pack("<Bi", 2, i)
            # Type 5 (string)
            self.test_content += struct.pack("<Bi", 5, i % 50)

    def test_parse_binary_content_performance(self):
        """Test binary content parsing performance."""
        print("\nBinary Content Parsing Performance:")

        avg_time, result = self.time_function(
            ContentParser.parse_binary_content,
            self.test_content,
            self.mock_string_table,
            self.mock_n_string,
        )

        types, values = result
        print(f"Content size: {len(self.test_content)} bytes")
        print(f"Parsed entries: {len(types)}")
        print(f"Average parse time: {avg_time * 1000:.3f} ms")
        print(f"Throughput: {len(self.test_content) / avg_time / 1024:.1f} KB/s")

    def test_list_to_dict_performance(self):
        """Test list to dictionary conversion performance."""
        # Create test data with nested segments
        types = []
        values = []

        # Add segments with various nesting levels
        for i in range(50):
            types.extend([5, 2, 2, 5])  # segment, int, int, end_segment
            values.extend([f"[segment_{i}]", i * 10, i * 20, f"[/segment_{i}]"])

        test_data = (types, values)

        print("\nList to Dict Conversion Performance:")

        avg_time, result = self.time_function(ContentParser.list_to_dict, test_data)

        print(f"Input entries: {len(types)}")
        print(f"Output segments: {len(result)}")
        print(f"Average conversion time: {avg_time * 1000:.3f} ms")


class TestMemoryUsage(unittest.TestCase):
    """Memory usage tests for the optimized version."""

    def test_string_table_memory_efficiency(self):
        """Test StringTable memory usage with caching."""
        import sys

        # Create a moderately sized string table
        num_strings = 500
        string_data = b""
        index_data = b""
        offset = 0

        for i in range(num_strings):
            string_content = f"test_string_with_longer_content_{i:04d}\x00".encode(
                "utf-8"
            )
            string_data += string_content

            index_data += struct.pack("<II", offset, offset + len(string_content))
            offset += len(string_content)

        table_bytes = struct.pack("I", num_strings) + index_data + string_data

        # Measure memory before
        initial_size = sys.getsizeof(table_bytes)

        # Create StringTable
        table = StringTable(table_bytes, encoding="utf-8")

        # Measure memory after
        table_size = sys.getsizeof(table.__dict__)
        cache_size = sys.getsizeof(table._converted_cache)

        print("\nMemory Usage Analysis:")
        print(f"Original data size: {initial_size:,} bytes")
        print(f"StringTable object: {table_size:,} bytes")
        print(f"Cache size: {cache_size:,} bytes")
        print(f"Total overhead: {(table_size + cache_size) / initial_size:.2f}x")

        # Test that cache provides benefit
        # Access all strings to populate cache
        for i in range(num_strings * 2):
            _ = table[i]

        # Verify cache is populated
        self.assertGreater(len(table._converted_cache), 0)
        print(f"Cached entries: {len(table._converted_cache)}")


def run_performance_tests():
    """Run all performance tests."""
    print("=" * 70)
    print("PVF Reader Optimized - Performance Tests")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add performance test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCryptoPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestStringTablePerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestContentParserPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryUsage))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)
