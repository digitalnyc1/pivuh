import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

_logger = logging.getLogger(__name__)

_P = ParamSpec("_P")
_T = TypeVar("_T")


def traced(
    level: int = logging.DEBUG, show_args: bool = False
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    def decorator(fn: Callable[_P, _T]) -> Callable[_P, _T]:
        qual = fn.__qualname__

        @wraps(fn)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            if _logger.isEnabledFor(level):
                if show_args:
                    _logger.log(
                        level,
                        "traced: -> %s args=%r kwargs=%r",
                        qual,
                        args[1:] if args else args,
                        kwargs,
                    )
                else:
                    _logger.log(level, "traced: -> %s", qual)
                t0 = time.perf_counter()
                try:
                    return fn(*args, **kwargs)
                finally:
                    dt_ms = (time.perf_counter() - t0) * 1000
                    _logger.log(level, "traced: <- %s (%.1f ms)", qual, dt_ms)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
