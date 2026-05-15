from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import load_json


SCHEMA_DIR = Path(__file__).resolve().parents[1] / "data" / "schemas"


class ValidationError(ValueError):
    pass


def validate_file(path: str | Path, schema_name: str) -> None:
    payload = load_json(path)
    schema = load_json(SCHEMA_DIR / schema_name)
    errors = validate_payload(payload, schema)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValidationError(f"{path} failed schema validation:\n{joined}")


def validate_payload(payload: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type and not _matches_type(payload, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(payload).__name__}")
        return errors

    if expected_type == "object":
        required = schema.get("required", [])
        for key in required:
            if key not in payload:
                errors.append(f"{path}.{key}: missing required field")
        properties = schema.get("properties", {})
        for key, value_schema in properties.items():
            if isinstance(payload, dict) and key in payload:
                errors.extend(validate_payload(payload[key], value_schema, f"{path}.{key}"))

    if expected_type == "array" and isinstance(payload, list):
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(payload):
                errors.extend(validate_payload(item, item_schema, f"{path}[{index}]"))

    return errors


def _matches_type(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True
