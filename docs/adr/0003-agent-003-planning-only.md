# ADR-0003: AGENT-003 is a Planning Agent — It Never Acquires or Evaluates

**Date**: 2026-08-17  
**Status**: `ACCEPTED`  
**Deciders**: Timonelo Architecture Group

---

## Context

The Knowledge Factory requires a mechanism to decide **what to acquire next**, distinct from
the agents that discover sources (AGENT-001) and ingest them (AGENT-002).

Without a planning layer, acquisition order is arbitrary. The factory may repeatedly ingest
low-value documents while high-value documents (those that would resolve many UNKNOWN statements)
remain unacquired.

A naive solution would be to extend AGENT-001 with prioritisation logic. This was considered
and rejected: AGENT-001's role is discovery and classification of individual candidates.
Giving it cross-graph planning awareness would violate single-responsibility.

---

## Decision

A new agent, **AGENT-003 (Coverage Planner)**, is introduced with a strictly bounded role:

> Given the current statement inventory, unknown register, and authority matrix, compute
> a ranked Evidence Acquisition Plan. Return it as structured JSON.

AGENT-003 never searches the internet, never downloads documents, never assigns trust,
and never creates statements.

Its output is consumed by AGENT-001 as an acquisition backlog.

---

## Rationale

**Single responsibility**: Each agent does one thing. AGENT-001 discovers. AGENT-002 ingests.
AGENT-003 plans. The Truth Engine evaluates.

**Determinism**: The planner's algorithm (gain = count of unknown predicates addressable
by a document class) is fully reproducible given the same inputs. No randomness, no I/O.

**Boundary preservation**: By making the planner a separate agent with its own input/output
schemas, it is impossible for planning logic to accidentally invoke acquisition or truth
evaluation.

---

## Consequences

**Positive**:
- Acquisition order is now principled: highest expected knowledge gain is always next.
- Planning logic is independently testable without any filesystem or network access.
- AGENT-001 can consume the roadmap as a typed, schema-validated backlog.

**Negative**:
- The authority matrix must be maintained manually: someone must declare which document
  classes can address which predicates. This is operational overhead.

**Neutral**:
- Two new schemas are added: `coverage-plan-request.schema.json` and
  `evidence-acquisition-plan.schema.json`. No existing schemas are modified.

---

## Compliance

Enforced by CI tests in `tests/test_coverage_planner.py`:

- `test_planner_does_not_produce_trust_fields`
- `test_planner_does_not_modify_request`
- `test_empty_authority_matrix_raises`
- All ranking and coverage computation tests are fully deterministic.
