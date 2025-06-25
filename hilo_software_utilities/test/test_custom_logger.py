import os
import logging
import tempfile
import pytest
from unittest import mock
from hilo_software_utilities.custom_logger import (
    init_logging, setup_logging_handlers,
    CustomFormatter, CUSTOM_LEVEL_NUM, CUSTOM_LEVEL_NAME
)

def test_setup_logging_handlers_rotate_success():
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        handlers = setup_logging_handlers(tmpfile.name, True, 1)
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)
        assert any(isinstance(h, logging.handlers.TimedRotatingFileHandler) for h in handlers)

def test_setup_logging_handlers_no_rotate_success():
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        handlers = setup_logging_handlers(tmpfile.name, False, 1)
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)
        assert not any(isinstance(h, logging.handlers.TimedRotatingFileHandler) for h in handlers)

def test_setup_logging_handlers_0_backup_success():
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        handlers = setup_logging_handlers(tmpfile.name, False, 0)
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)
        assert not any(isinstance(h, logging.handlers.TimedRotatingFileHandler) for h in handlers)

def test_setup_logging_handlers_rotate_failure(monkeypatch):
    monkeypatch.setattr("logging.handlers.TimedRotatingFileHandler", mock.MagicMock(side_effect=OSError("fail")))
    handlers = setup_logging_handlers("/invalid/path/to/logfile.log", True, 1)
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)

def test_custom_log_level(caplog):
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        logger = init_logging(tmpfile.name)
        with caplog.at_level(CUSTOM_LEVEL_NUM):
            logger.custom("This is a custom message.")
        assert "This is a custom message." in caplog.text
        assert CUSTOM_LEVEL_NAME in caplog.text

def test_formatter_formats_correctly():
    formatter = CustomFormatter(
        fmt="%(levelname)s: %(message)s",
        info_fmt="INFO_ONLY: %(message)s",
        custom_fmt="CUSTOM_ONLY: %(message)s"
    )

    record_info = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Info msg", args=(), exc_info=None)
    record_custom = logging.LogRecord(name="test", level=CUSTOM_LEVEL_NUM, pathname="", lineno=0, msg="Custom msg", args=(), exc_info=None)
    record_error = logging.LogRecord(name="test", level=logging.ERROR, pathname="", lineno=0, msg="Error msg", args=(), exc_info=None)

    assert formatter.format(record_info) == "INFO_ONLY: Info msg"
    assert formatter.format(record_custom) == "CUSTOM_ONLY: Custom msg"
    assert formatter.format(record_error) == "ERROR: Error msg"

def test_logger_logs_all_levels(tmp_path):
    log_file = tmp_path / "test.log"
    logger = init_logging(log_file=str(log_file), level=logging.INFO)
    logger.info("info message")
    logger.error("error message")
    logger.custom("custom message")

    logger.handlers[0].flush()
    with open(log_file, "r") as f:
        content = f.read()

    assert "info message" in content
    assert "error message" in content
    assert "custom message" in content
