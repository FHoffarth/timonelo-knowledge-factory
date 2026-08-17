"""
scripts/validate_schemas.py

Validates that every JSON Schema file in schemas/ is structurally valid
Draft-07. This script is run by CI and must pass before any release.

Usage:
    python scripts/validate_schemas.py
"""

import json
import os
import sys

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: jsonschema is required. Run: pip install jsonschema==4.23.0")
    sys.exit(1)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(REPO_ROOT, "schemas")

REQUIRED_SCHEMAS = [
    "artifact-candidate.schema.json",
    "artifact.schema.json",
    "statement.schema.json",
    "coverage-plan-request.schema.json",
    "evidence-acquisition-plan.schema.json",
]


def main() -> None:
    errors: list[str] = []

    for schema_name in REQUIRED_SCHEMAS:
        schema_path = os.path.join(SCHEMAS_DIR, schema_name)

        if not os.path.exists(schema_path):
            errors.append(f"  MISSING  {schema_name}")
            continue

        with open(schema_path, "r", encoding="utf-8") as f:
            try:
                schema = json.load(f)
            except json.JSONDecodeError as exc:
                errors.append(f"  INVALID JSON  {schema_name}: {exc}")
                continue

        if schema.get("$schema") != "http://json-schema.org/draft-07/schema#":
            errors.append(
                f"  WRONG $schema  {schema_name}: "
                f"expected Draft-07, got {schema.get('$schema')!r}"
            )

        try:
            Draft7Validator.check_schema(schema)
            print(f"  OK  {schema_name}")
        except jsonschema.exceptions.SchemaError as exc:
            errors.append(f"  SCHEMA ERROR  {schema_name}: {exc.message}")

    if errors:
        print("\nSchema validation FAILED:")
        for e in errors:
            print(e)
        sys.exit(1)

    print(f"\n{len(REQUIRED_SCHEMAS)} schemas validated successfully.")


if __name__ == "__main__":
    main()
