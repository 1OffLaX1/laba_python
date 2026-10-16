from functools import wraps
from time import perf_counter
from typing import Callable


def log_call(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"[LOG] {function.__name__}")
        return function(*args, **kwargs)
    return wrapper


def timed(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            print(f"[TIME] {function.__name__}: {perf_counter() - start:.6f} с")
    return wrapper


def require_status(required) -> Callable:
    def decorate(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if self.status != required:
                raise ValueError(f"Операция разрешена только в состоянии: {required.value}")
            return function(self, *args, **kwargs)
        return wrapper
    return decorate
