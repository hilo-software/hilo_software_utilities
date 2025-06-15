# projects/utilities/test/test_send_mail.py
import pytest
import smtplib
from unittest.mock import patch, MagicMock
from email.message import EmailMessage
from utilities import send_mail  # Adjusted import


@pytest.fixture
def dummy_email_msg():
    msg = EmailMessage()
    msg.set_content("Test Content")
    msg['Subject'] = "Test Subject"
    msg['From'] = "test@example.com"
    msg['To'] = "test@example.com"
    return msg


@patch("smtplib.SMTP")
def test_send_success(mock_smtp, dummy_email_msg):
    send_mail.send("test@example.com", "test@example.com", "dummy_app_key", dummy_email_msg)
    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    instance = mock_smtp.return_value
    assert instance.login.called
    assert instance.sendmail.called
    assert instance.close.called


@patch("smtplib.SMTP", side_effect=smtplib.SMTPException("SMTP failed"))
def test_send_smtp_exception(mock_smtp, dummy_email_msg, caplog):
    send_mail.send("test@example.com", "test@example.com", "dummy_app_key", dummy_email_msg)
    assert "SMTP ERROR" in caplog.text


@patch("smtplib.SMTP", side_effect=Exception("General failure"))
def test_send_general_exception(mock_smtp, dummy_email_msg, caplog):
    send_mail.send("test@example.com", "test@example.com", "dummy_app_key", dummy_email_msg)
    assert "General ERROR" in caplog.text


@patch("utilities.send_mail.smtplib.SMTP", side_effect=smtplib.SMTPException("SMTP failed"))
def test_send_text_email(mock_send):
    send_mail.send_text_email("test@example.com", "dummy_app_key", "Test Subject", "This is a test.")
    assert mock_send.called


@patch("utilities.send_mail.smtplib.SMTP", side_effect=smtplib.SMTPException("SMTP failed"))
def test_send_file_email_success(mock_send_text, tmp_path):
    test_file = tmp_path / "log.txt"
    test_file.write_text("Log content")
    send_mail.send_file_email("test@example.com", "dummy_app_key", "Log Subject", str(test_file))
    mock_send_text.assert_called_once()


def test_send_file_email_failure(tmp_path, caplog):
    bad_file = tmp_path / "nonexistent.txt"
    send_mail.send_file_email("test@example.com", "dummy_app_key", "Log Subject", str(bad_file))
    assert "Could not read file" in caplog.text
