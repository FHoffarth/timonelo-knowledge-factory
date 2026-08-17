# Changelog

All notable changes to the Timonelo Knowledge Factory are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning 2.0.0](https://semver.org/).

---

## [Unreleased]

---

## [1.0.0] — 2026-08-17

### Added
- Initial repository structure: `agents/`, `schemas/`, `examples/`, `src/`, `tests/`, `scripts/`, `docs/adr/`.
- `AGENT-001` (Evidence Intelligence): full specification — Mission, System Prompt, Output Schema, Tests, Changelog.
- `AGENT-002` (Artifact Intake): full specification — Mission, System Prompt, Output Schema, Tests, Changelog.
- JSON Schema Draft-07 contracts: `artifact-candidate.schema.json`, `artifact.schema.json`, `statement.schema.json`.
- `TruthEngineBridge` connector (`src/connectors/truth_engine_bridge.py`): deterministic `ArtifactCandidate → RegisteredArtifact` transformation. No trust evaluation.
- 22-test suite covering connector mechanics and responsibility boundary enforcement.
- CI workflow (`.github/workflows/ci.yml`): tests on Python 3.11+3.12, schema validation, lint.
- Release workflow (`.github/workflows/release.yml`): full validation gate before GitHub Release creation.
- `scripts/validate_schemas.py`: CI script asserting Draft-07 compliance for all schemas.
- `scripts/validate_examples.py`: CI script validating all example files against schemas.
- `CONTRIBUTING.md`: boundary law, workflow, ADR requirement, versioning, forbidden actions.
- `docs/adr/0000-template.md`: ADR template.
- `docs/adr/0001-connector-does-not-evaluate-trust.md`: records boundary-hardening decision.
- `docs/adr/0002-json-schema-draft-07.md`: records schema dialect decision.

### Changed
- `artifact.schema.json`: removed `trust_level` from `provenance.required` (boundary-hardening sprint).
- `TruthEngineBridge`: removed `TRUST_LEVEL_MAP` and synthetic authority string generation.

### Removed
- `provenance.trust_level` from `RegisteredArtifact` contract — moved to Truth Engine responsibility.
