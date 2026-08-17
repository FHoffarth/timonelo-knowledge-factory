# Contributing to Timonelo Knowledge Factory

Thank you for contributing. This document defines the only accepted workflow.

---

## Boundary Law

Before any contribution, internalize the responsibility boundary:

| Layer | Responsibility |
|---|---|
| **Knowledge Factory** | Evidence discovery, candidate registration, schema enforcement, connector mechanics |
| **Truth Engine** | Trust evaluation, credibility scoring, statement extraction, review, answer publication |

**The connector never evaluates trust. The Truth Engine never touches raw candidates.**  
A contribution that crosses this boundary will be rejected regardless of quality.

---

## Workflow

### 1. Branch

```bash
git checkout -b feat/your-topic        # new capability
git checkout -b fix/your-bug           # bug fix
git checkout -b docs/your-change       # documentation only
git checkout -b adr/NNN-decision-name  # Architecture Decision Record
```

No work on `main` directly. Ever.

### 2. Write Tests First

Every code change requires a corresponding test. Tests live in `tests/`.

- Tests must pass locally before opening a pull request.
- Boundary tests are mandatory for any change touching `src/connectors/`.

```bash
python -m unittest discover -s tests -v
```

### 3. Validate Schemas

If you add or modify a JSON Schema:

```bash
pip install jsonschema==4.23.0
python scripts/validate_schemas.py
python scripts/validate_examples.py
```

### 4. Lint

```bash
pip install ruff==0.5.7
ruff check src/ tests/ scripts/
```

### 5. Pull Request

- Title: `type(scope): short description` — e.g. `feat(connector): add JSON fallback hash`
- Description must state: what changed, why, and which tests cover it.
- Link to any relevant ADR if the change involves a design decision.

### 6. Merge

Only squash-merge into `main`. Commit message = PR title.

---

## Architecture Decision Records

Significant decisions are recorded in `docs/adr/`.  
Use `ADR-NNN-title.md`. Copy the template from `docs/adr/0000-template.md`.

An ADR is required when:
- A new agent is introduced.
- A schema field changes meaning.
- A responsibility boundary is redefined.
- The connector output contract changes.

---

## Versioning

This repository follows [Semantic Versioning 2.0.0](https://semver.org/):

| Change | Version bump |
|---|---|
| Breaking schema change, removed field | `MAJOR` |
| New agent, new schema field (backward-compatible) | `MINOR` |
| Bug fix, test addition, documentation | `PATCH` |

Releases are created by pushing a `vMAJOR.MINOR.PATCH` tag to `main`.  
The release workflow handles the rest.

---

## What Is Never Acceptable

- Fabricating publisher or authority strings when none are declared.
- Adding `trust_level`, `authority_level`, or any credibility field to the connector.
- Merging without tests.
- Direct pushes to `main`.
