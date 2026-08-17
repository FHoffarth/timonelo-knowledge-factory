# ADR-0002: JSON Schema Draft-07 as the Sole Schema Standard

**Date**: 2026-08-17  
**Status**: `ACCEPTED`  
**Deciders**: Timonelo Architecture Group

---

## Context

The Knowledge Factory produces structured JSON payloads at three stages of the pipeline:
`ArtifactCandidate`, `IngestedArtifact`, and `KnowledgeStatement`. Each stage requires
a formal contract that can be validated automatically in CI and by agents at runtime.

Multiple schema dialects are available: Draft-04, Draft-06, Draft-07, Draft 2019-09, Draft 2020-12.

---

## Decision

All schemas in `schemas/` use **JSON Schema Draft-07** exclusively, declared via:

```json
"$schema": "http://json-schema.org/draft-07/schema#"
```

---

## Rationale

- Draft-07 is the widest-supported dialect across Python (`jsonschema`), JavaScript, and Go tooling.
- Draft-07 introduces `if/then/else` and `readOnly`/`writeOnly` — sufficient for our contracts.
- Draft 2019-09 and 2020-12 are not yet uniformly supported across CI validators.
- Consistency across all three schemas eliminates dialect-mismatch bugs.

---

## Consequences

**Positive**:
- Single validator version in CI (`jsonschema==4.23.0 Draft7Validator`).
- All agents can validate their output against one known dialect.

**Negative**:
- Some newer features (e.g. `$dynamicRef`) are unavailable.

---

## Compliance

Enforced by `scripts/validate_schemas.py`, which asserts `$schema == Draft-07` for every
file in `schemas/` and calls `Draft7Validator.check_schema()`. This runs on every CI push.
