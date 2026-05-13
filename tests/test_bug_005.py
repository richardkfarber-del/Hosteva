import pytest

def test_gunicorn_installed():
    assert 'pip install gunicorn' in open('/path/to/dockerfile').read()