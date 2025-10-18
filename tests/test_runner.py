#!/usr/bin/env python3
"""
Test runner for PVF Reader optimized version.

This script runs all unit tests and provides detailed reporting.
"""

import logging
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests():
    """Run all tests and return results."""
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

    # Discover and load tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2, stream=sys.stdout, descriptions=True, failfast=False
    )

    print('=' * 70)
    print('Running PVF Reader Optimized Tests')
    print('=' * 70)

    result = runner.run(suite)

    # Print summary
    print('\n' + '=' * 70)
    print('Test Summary:')
    print(f'Tests run: {result.testsRun}')
    print(f'Failures: {len(result.failures)}')
    print(f'Errors: {len(result.errors)}')
    print(f'Skipped: {len(result.skipped) if hasattr(result, "skipped") else 0}')

    if result.failures:
        print('\nFailures:')
        for test, traceback in result.failures:
            print(f'  - {test}: {traceback.split("AssertionError:")[-1].strip()}')

    if result.errors:
        print('\nErrors:')
        for test, traceback in result.errors:
            print(f'  - {test}: {traceback.split("Exception:")[-1].strip()}')

    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors))
        / result.testsRun
        * 100
    )
    print(f'\nSuccess rate: {success_rate:.1f}%')
    print('=' * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
