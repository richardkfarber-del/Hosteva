"""Shared server-side password policy for every set-password path (US-012).

Rules (Iron Man AUTH_PASSWORD_EMAIL): min 8, max 128, reject digits-only,
reject whitespace-only. Never echo the submitted password in errors.
"""
from __future__ import annotations

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

POLICY_HINT = "At least 8 characters, not numbers only (max 128)."


class PasswordPolicyError(ValueError):
    """Password failed the shared policy. str(exc) is safe to show to clients."""


def validate_password(password: str | None) -> str:
    """Return password if it meets policy; raise PasswordPolicyError otherwise."""
    if not isinstance(password, str):
        raise PasswordPolicyError("Password does not meet requirements.")
    if not password or password.strip() == "":
        raise PasswordPolicyError("Password cannot be only whitespace.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError("Password must be at least 8 characters.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordPolicyError("Password must be at most 128 characters.")
    if password.isdigit():
        raise PasswordPolicyError("Password cannot be numbers only.")
    return password


PASSWORD_FIELD_NAMES = frozenset({
    "password", "new_password", "confirm_password", "current_password",
})


def redact_validation_errors(errors: list) -> list:
    """Strip submitted password values from Pydantic 422 payloads."""
    cleaned = []
    for err in errors:
        item = dict(err)
        loc = item.get("loc") or ()
        if any(str(part) in PASSWORD_FIELD_NAMES for part in loc):
            item.pop("input", None)
        cleaned.append(item)
    return cleaned
