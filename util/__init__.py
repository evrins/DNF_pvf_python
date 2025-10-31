import hashlib
import time

from loguru import logger


def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end = time.perf_counter_ns()
        print(f'{func.__name__} took {(end - start) / 1_000_000.0:.4f} ms to run.')
        return result

    return wrapper


def calculate_hash_of_file(fp: str) -> str:
    sha1 = hashlib.sha1()
    try:
        with open(fp, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha1.update(byte_block)
            full_hash = sha1.hexdigest()
            return full_hash[:8]
    except IOError:
        logger.error(f'fail to read file {fp}')
        return ''


def test_calculate_hash_of_file() -> str:
    fp = '/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf'
    res = calculate_hash_of_file(fp)
    print(f'{fp}: {res}')
