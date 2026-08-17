# Timonelo Knowledge Factory

> **Autonomous Evidence Ingestion, Artifact Extraction, and Graph Compilation Pipeline for Naval Architecture and Cruise Intelligence.**

---

## Overview

The **Timonelo Knowledge Factory** is the ingestion and verification subsystem of the Timonelo platform. It translates unstructured naval shipyard General Arrangements (GA), port authority dispatches, maritime registries, and stateroom acoustic layouts into cryptographically verifiable, schema-conforming knowledge graphs.

```
Knowledge Factory Pipeline
├── docs/       # Architecture & Roadmap specifications
├── agents/     # Deterministic AI Agent specs, prompts & contracts
├── schemas/    # Formal JSON Schemas (Artifacts, Candidates, Statements)
├── examples/   # Real-world candidate extractions (e.g. MSC Bellissima)
├── tests/      # Automated verification and acquisition test suites
└── scripts/    # Ingestion runners and compilation tools
```

---

## Autonomous Agent Network

| Agent ID | Name | Role & Objective | Status |
| :--- | :--- | :--- | :--- |
| **`AGENT-001`** | **Evidence Intelligence** | Discovers, ranks, and classifies primary maritime sources and candidate artifacts. | `ACTIVE` |
| **`AGENT-002`** | **Artifact Intake** | Ingests, normalizes, and validates primary sources against formal JSON schemas. | `ACTIVE` |

---

## Core Guarantees

1. **Zero Hallucination**: No statement enters the master graph without a traceable primary source reference (shipyard blueprint, IMO registry, or port dispatch).
2. **Negative Intelligence**: Systematic identification of bottleneck elevators, noise sandwich decks, and terminal transfer risks.
3. **Class Inheritance**: Unambiguous tracking of whether stateroom metrics are blueprint-scanned or inherited from a class reference model.

---

## Quickstart

```bash
# Validate schemas
python -m unittest discover -s tests
```

---

*© 2026 Timonelo Naval Architecture & Systems Group.*