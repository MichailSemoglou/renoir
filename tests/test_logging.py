"""
Tests for the structured logging helper.
"""

import io
import logging

import pytest

import renoir
from renoir.logging import setup_notebook_logging


@pytest.fixture
def clean_renoir_logger():
    """Snapshot and restore the renoir logger's handlers around each test."""
    logger = logging.getLogger("renoir")
    saved_handlers = list(logger.handlers)
    saved_level = logger.level
    logger.handlers = []
    yield logger
    logger.handlers = saved_handlers
    logger.setLevel(saved_level)


def test_attaches_single_stream_handler(clean_renoir_logger):
    """One call attaches exactly one StreamHandler."""
    setup_notebook_logging()
    handlers = clean_renoir_logger.handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)


def test_idempotent_on_same_stream(clean_renoir_logger):
    """Repeated calls with the same stream do not add duplicate handlers."""
    setup_notebook_logging()
    setup_notebook_logging()
    setup_notebook_logging()
    assert len(clean_renoir_logger.handlers) == 1


def test_distinct_stream_attaches_second_handler(clean_renoir_logger):
    """A different stream counts as a different sink and gets a handler."""
    setup_notebook_logging()
    setup_notebook_logging(stream=io.StringIO())
    assert len(clean_renoir_logger.handlers) == 2


def test_handler_level_and_formatter(clean_renoir_logger):
    """The handler carries the requested level and the house format."""
    setup_notebook_logging(level=logging.DEBUG)
    handler = clean_renoir_logger.handlers[0]
    assert handler.level == logging.DEBUG
    assert handler.formatter is not None
    assert "%(name)s" in handler.formatter._fmt


def test_messages_reach_the_stream(clean_renoir_logger):
    """A logged message is written to the attached stream."""
    stream = io.StringIO()
    setup_notebook_logging(stream=stream)
    clean_renoir_logger.setLevel(logging.INFO)
    logging.getLogger("renoir.demo").info("palette ready")
    assert "palette ready" in stream.getvalue()


def test_exported_at_package_level():
    """The helper is part of the public renoir namespace."""
    assert callable(renoir.setup_notebook_logging)
