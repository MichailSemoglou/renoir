"""
Structured logging helpers for renoir.

Provides a convenience function that attaches a :class:`logging.StreamHandler`
to the ``renoir`` namespace logger so progress messages appear in Jupyter
notebooks and interactive sessions without additional configuration.

Example::

    >>> import renoir
    >>> renoir.setup_notebook_logging()
    >>> # All renoir loggers now write to stderr

The function is idempotent -- calling it multiple times does not add
duplicate handlers.
"""

import logging
import sys
from typing import IO, Optional


def setup_notebook_logging(
    level: int = logging.INFO,
    stream: Optional[IO[str]] = None,
) -> None:
    """
    Attach a :class:`logging.StreamHandler` to the ``renoir`` root logger.

    Designed for Jupyter notebooks and interactive sessions where the default
    ``logging.lastResort`` handler may not be active.

    Args:
        level: Log level for the handler (default: ``logging.INFO``). Use
            ``logging.DEBUG`` for detailed diagnostics.
        stream: Output stream (default: ``sys.stderr``). Use
            ``sys.stdout`` to redirect to the notebook cell output area.

    Returns:
        None
    """
    if stream is None:
        stream = sys.stderr

    root = logging.getLogger("renoir")
    for existing in root.handlers:
        if isinstance(existing, logging.StreamHandler) and existing.stream is stream:
            return

    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(name)s [%(levelname)s] %(message)s"))
    root.addHandler(handler)
