"""
scripts/validate_examples.py

Validates every JSON file in examples/ against its declared schema.
Each example must declare a top-level "$schema" field that resolves
to a file in schemas/.

Usage:
    python scripts/validate_examples.py
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
EXAMPLES_DIR = os.path.join(REPO_ROOT, "examples")

# Examples that are arrays validate each element against the candidate schema.
ARRAY_EXAMPLES: dict[str, str] = {
    "bellissima_candidates.json": "artifact-candidate.schema.json",
}


def load_schema(name: str) -> dict:
    path = os.path.join(SCHEMAS_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    errors: list[str] = []
    validated = 0

    for filename, schema_name in ARRAY_EXAMPLES.items():
        example_path = os.path.join(EXAMPLES_DIR, filename)

        if not os.path.exists(example_path):
            errors.append(f"  MISSING  examples/{filename}")
            continue

        schema = load_schema(schema_name)
        validator = Draft7Validator(schema)

        with open(example_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as exc:
                errors.append(f"  INVALID JSON  examples/{filename}: {exc}")
                continue

        items = data if isinstance(data, list) else [data]
        for i, item in enumerate(items):
            item_errors = list(validator.iter_errors(item))
            if item_errors:
                for e in item_errors:
                    errors.append(
                        f"  INVALID  examples/{filename}[{i}]: "
                        f"{e.json_path} — {e.message}"
                    )
            else:
                validated += 1
                print(f"  OK  examples/{filename}[{i}] -> {schema_name}")

    if errors:
        print("\nExample validation FAILED:")
        for e in errors:
            print(e)
        sys.exit(1)

    print(f"\n{validated} example records validated successfully.")


if __name__ == "__main__":
    main()
