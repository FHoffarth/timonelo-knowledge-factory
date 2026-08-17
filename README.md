# Timonelo Knowledge Factory

> Autonomous evidence ingestion, artifact registration, and graph compilation pipeline  
> for naval architecture and cruise intelligence.

---

## Repository Structure

```text
timonelo-knowledge-factory/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Tests, schema validation, lint on every push & PR
│       └── release.yml     # Full validation → GitHub Release on semver tag
├── docs/
│   ├── adr/                # Architecture Decision Records
│   ├── architecture.md     # Pipeline diagram and evidence classification
│   └── roadmap.md          # Phased delivery plan
├── agents/
│   ├── AGENT-001-evidence-intelligence/
│   └── AGENT-002-artifact-intake/
├── schemas/                # JSON Schema Draft-07 contracts
│   ├── artifact-candidate.schema.json
│   ├── artifact.schema.json
│   └── statement.schema.json
├── src/
│   └── connectors/
│       └── truth_engine_bridge.py   # The only bridge: Candidate → Artifact
├── examples/               # Real candidate extractions (MSC Bellissima, Genoa)
├── scripts/
│   ├── validate_schemas.py # CI: validates all schemas are Draft-07 compliant
│   └── validate_examples.py# CI: validates examples against their schemas
└── tests/                  # Automated test suite (22 tests, stdlib only)
```

---

## Autonomous Agent Network

| Agent | Name | Role | Status |
|---|---|---|---|
| `AGENT-001` | Evidence Intelligence | Discovers, ranks, and classifies primary maritime sources | `ACTIVE` |
| `AGENT-002` | Artifact Intake | Ingests, normalizes, and validates primary sources | `ACTIVE` |

---

## Pipeline

```
AGENT-001 (Evidence Intelligence)
    ↓  ArtifactCandidate JSON
Truth Engine Connector Bridge   ← this repository
    ↓  RegisteredArtifact JSON
Truth Engine                    ← separate system
    ↓  Statements → Review → Published Answer
```

---

## Core Guarantees

1. **Zero hallucination**: No string is invented. Missing fields are omitted, not fabricated.
2. **Boundary law**: The connector performs only deterministic transformations. Trust evaluation belongs exclusively to the Truth Engine (see [ADR-0001](docs/adr/0001-connector-does-not-evaluate-trust.md)).
3. **Immutability**: `ArtifactCandidate` and `RegisteredArtifact` are independently addressable. The candidate is never mutated.

---

## CI Status

Every push to `main` and every pull request runs:
- Full test suite (Python 3.11 & 3.12)
- JSON Schema validation (`scripts/validate_schemas.py`)
- Example conformance validation (`scripts/validate_examples.py`)
- Lint (`ruff`)

---

## Quickstart

```bash
# Run test suite (no external dependencies required)
python -m unittest discover -s tests -v

# Register a candidate file
python src/connectors/truth_engine_bridge.py examples/bellissima_candidates.json
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Versioning

This repository follows [Semantic Versioning 2.0.0](https://semver.org/).  
Current version: **1.0.0** — see [CHANGELOG.md](CHANGELOG.md).

---

*© 2026 Timonelo Naval Architecture & Systems Group — MIT License*