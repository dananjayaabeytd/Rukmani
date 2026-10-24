"""
Logging setup — powered by loguru.

Call ``setup_logging()`` once when the app starts. Everywhere else, just::

    from loguru import logger
    logger.info("Hello")

Logs from third-party libraries that use Python's standard ``logging``
module (uvicorn, httpx, ...) are routed through loguru too, so all output
has the same format.
"""

import logging
import sys

from loguru import logger

_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>"
)


class _InterceptHandler(logging.Handler):
    """Forward standard-library log records to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str = "INFO") -> None:
    """Configure loguru for the whole process."""
    logger.remove()  # drop loguru's default handler so we control the format
    logger.add(sys.stderr, format=_FORMAT, level=level.upper(), backtrace=False, diagnose=False)
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    # These libraries log every HTTP request at INFO — too noisy for normal use.
    for noisy in ("httpx", "httpx2", "httpcore", "mcp", "openai", "groq"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
