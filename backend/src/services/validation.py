"""Validation utilities for input fields (names, descriptions, etc.).

Rules (from data-model spec):
- Name max length 100 characters
- Allowed characters: letters, numbers, space, underscore, hyphen, period
- Description optional; if provided trim surrounding whitespace
"""
import re

_NAME_RE = re.compile(r'^[A-Za-z0-9 _\-.]{1,100}$')

class ValidationError(ValueError):
    """Raised when validation fails."""


def validate_name(name: str) -> str:
    if name is None:
        raise ValidationError("Name required")
    name = name.strip()
    if not name:
        raise ValidationError("Name required")
    if len(name) > 100:
        raise ValidationError("Name too long (max 100)")
    if not _NAME_RE.match(name):
        raise ValidationError("Invalid characters in name")
    return name


def normalize_description(description: str | None) -> str | None:
    if description is None:
        return None
    d = description.strip()
    return d or None
