"""Shared CI/local pytest baseline for tests/.

Loaded before test modules in this directory. Individual modules may still
override DATABASE_URL / BILLING_ENABLED for isolation; success-path billing
tests must re-enable BILLING_ENABLED explicitly (later imports may set false).
"""
import os

from cryptography.fernet import Fernet

# Baseline env — mirrors app/tests/conftest.py; do not flip production billing.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_ci.db")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("JWT_SECRET_KEY", "TEST_SECRET_KEY")
os.environ.setdefault(
    "VIBRANIUM_ENCRYPTION_KEY",
    os.environ.get("VIBRANIUM_ENCRYPTION_KEY") or Fernet.generate_key().decode(),
)
# Default kill-switch OFF (prod-like). Tests that need checkout success set true.
os.environ.setdefault("BILLING_ENABLED", "false")
