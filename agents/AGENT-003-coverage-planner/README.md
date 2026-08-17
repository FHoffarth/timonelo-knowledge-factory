# AGENT-003: Coverage Planner

> **Determines which evidence artifact should be acquired next in order to maximise truthful knowledge growth.**

---

## 1. Mission

The Coverage Planner analyses the current state of the knowledge graph — how many statements are known, which are unknown, and which document classes are capable of resolving them — and produces a ranked **Evidence Acquisition Plan**.

It does not discover documents. It does not download documents. It does not evaluate truth. It only plans acquisition.

---

## 2. Position in the Pipeline

```
AGENT-001 (Evidence Intelligence)  ←── consumes the plan's roadmap as acquisition backlog
        ↑
AGENT-003 (Coverage Planner)       ← this agent
        ↑
Inputs: RegisteredArtifacts / StatementInventory / UnknownRegister / AuthorityMatrix
```

---

## 3. Responsibilities

1. **Compute statement coverage** — answered vs unknown, expressed as a percentage.
2. **Identify every UNKNOWN statement** — from the `unknown_register`.
3. **Map unknowns to document classes** — via the `authority_matrix`.
4. **Estimate expected knowledge gain** — count of unknowns resolvable per document class.
5. **Rank acquisition priorities** — highest expected gain first; alphabetical on ties.
6. **Produce an Evidence Acquisition Plan** — conforming to `evidence-acquisition-plan.schema.json`.

---

## 4. Forbidden Actions

| Forbidden | Reason |
|---|---|
| Search the internet | Acquisition is AGENT-001's responsibility |
| Download documents | Acquisition is AGENT-001's responsibility |
| Assign trust | Trust evaluation belongs to the Truth Engine |
| Create statements | Statement creation belongs to the Truth Engine |
| Answer passenger questions | Out of scope |
| Override the Truth Engine | Hard architectural boundary |

---

## 5. Input Contract

Conforms to [`schemas/coverage-plan-request.schema.json`](../../schemas/coverage-plan-request.schema.json).

Key fields:

| Field | Type | Description |
|---|---|---|
| `entity_slug` | string | Entity being planned for |
| `statement_inventory` | object | `{ answered, unknown }` counts |
| `unknown_register` | array | Every unresolved `{ predicate, subject_slug }` |
| `authority_matrix` | array | `{ document_class, addressable_predicates[] }` entries |
| `registered_artifact_ids` | array | Already-ingested artifact IDs (avoid re-acquisition) |

---

## 6. Output Contract

Conforms to [`schemas/evidence-acquisition-plan.schema.json`](../../schemas/evidence-acquisition-plan.schema.json).

```json
{
  "entity_slug": "msc-bellissima",
  "computed_at": "2026-08-17T18:00:00Z",
  "coverage": {
    "answered": 418,
    "unknown": 297,
    "coverage_percent": 58.5
  },
  "recommended_next_document": {
    "document_class": "General Arrangement Drawing",
    "expected_new_statements": 41,
    "expected_unknown_reduction_percent": 13.8
  },
  "roadmap": [
    { "priority": 1, "document_class": "General Arrangement Drawing",  "expected_new_statements": 41, "expected_unknown_reduction_percent": 13.8 },
    { "priority": 2, "document_class": "Accessibility Guide",           "expected_new_statements": 22, "expected_unknown_reduction_percent": 7.4 },
    { "priority": 3, "document_class": "Port Authority Berth Notice",   "expected_new_statements": 18, "expected_unknown_reduction_percent": 6.1 }
  ]
}
```

---

## 6. Files in this Module

- [`SYSTEM_PROMPT.md`](./SYSTEM_PROMPT.md) — Runtime instructions for LLM invocation.
- [`OUTPUT_SCHEMA.json`](./OUTPUT_SCHEMA.json) — Dedicated output schema copy.
- [`TESTS.md`](./TESTS.md) — Test scenario specifications.
- [`CHANGELOG.md`](./CHANGELOG.md) — Version history.

---

## 7. Implementation

[`src/agents/coverage_planner.py`](../../src/agents/coverage_planner.py)

```bash
python src/agents/coverage_planner.py examples/bellissima_plan_request.json
```
