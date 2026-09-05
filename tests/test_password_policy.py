"""US-012 shared password policy."""
from app.core.password_policy import validate_password, PasswordPolicyError
import pytest


@pytest.mark.parametrize(
    "bad",
    [
        "1234",
        "0000",
        "12345678",
        "abcdefgh7"[:4],  # short via slice still < 8... use explicit:
        "short",
        "       ",
        "\t\t\t\t",
        "1" * 129,
        "",
        None,
    ],
)
def test_policy_rejects_weak(bad):
    with pytest.raises(PasswordPolicyError) as exc:
        validate_password(bad)
    assert str(exc.value)
    if isinstance(bad, str) and bad.strip():
        assert bad not in str(exc.value)


def test_policy_rejects_digits_only_eight():
    with pytest.raises(PasswordPolicyError, match="numbers only"):
        validate_password("12345678")


def test_policy_rejects_too_short():
    with pytest.raises(PasswordPolicyError, match="at least 8"):
        validate_password("abcdefg")


def test_policy_rejects_whitespace_only():
    with pytest.raises(PasswordPolicyError, match="whitespace"):
        validate_password("        ")


def test_policy_rejects_too_long():
    with pytest.raises(PasswordPolicyError, match="at most 128"):
        validate_password("a" * 129)


def test_policy_accepts_valid():
    assert validate_password("password1") == "password1"
    assert validate_password("abcdefgh") == "abcdefgh"
    assert validate_password("A" * 128) == "A" * 128
