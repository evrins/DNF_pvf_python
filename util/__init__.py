import time


def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end = time.perf_counter_ns()
        print(f'{func.__name__} took {end - start} nanoseconds to run.')
        return result

    return wrapper
