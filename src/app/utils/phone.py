from typing import Any


def stringify_phone(value: Any):
    if hasattr(value, 'phone_number'):
        return getattr(value, 'phone_number', None)

    if isinstance(value, str):
        return value

    raise ValueError('Please provide a valid phone number')


def validate_phones(value: Any):
    if isinstance(value, list):
        return [stringify_phone(phone) for phone in value]

    return [stringify_phone(value)]
