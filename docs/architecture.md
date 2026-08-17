# Knowledge Factory Architecture

> **Deterministic Multi-Stage Acquisition, Schema Enforcement, and Knowledge Graph Compilation.**

---

## 1. Architectural Pipeline

```mermaid
flowchart TD
    subgraph Discovery ["1. Evidence Intelligence (AGENT-001)"]
        S1[Shipyard GAs] --> AG1[AGENT-001: Evidence Intelligence]
        S2[Port Authority Portals] --> AG1
        S3[IMO Registries] --> AG1
        AG1 --> CAND[Artifact Candidates\nartifact-candidate.schema.json]
    end

    subgraph Intake ["2. Artifact Intake (AGENT-002)"]
        CAND --> AG2[AGENT-002: Artifact Intake]
        AG2 --> NORM[Normalized Artifacts\nartifact.schema.json]
    end

    subgraph Graph ["3. Graph Synthesis & Statements"]
        NORM --> EXTRACT[Statement Extraction\nstatement.schema.json]
        EXTRACT --> KG[(Cruise Knowledge Graph\nNodes, Edges, Provenance)]
    end

    subgraph Compiler ["4. Master Compilation"]
        KG --> COMP[Compiler Engine]
        COMP --> DB[(Master DB / Frontend Bridges)]
    end
```

---

## 2. Evidence Classification Hierarchy

Every incoming piece of evidence is graded on a deterministic 4-tier scale:

1. **`OFFICIAL_SHIPYARD` (Weight: 1.00)**: Original general arrangements, builder sea-trial protocols, Chantiers de l'Atlantique / Fincantieri technical dossiers.
2. **`OFFICIAL_AUTHORITY` (Weight: 0.95)**: UN/LOCODE, Port Authority notices, Harbour Master dispatches, Coast Guard declarations.
3. **`OPERATOR_TECHNICAL` (Weight: 0.85)**: Cruise line official deck vector schematics, muster safety plans.
4. **`DECK_OFFICER_LOG` (Weight: 0.80)**: Verified bridge watch logs, empirical gangway deck observations.

---

## 3. Schema Enforcement & Quality Gates

All artifacts must satisfy rigid JSON Schema contracts before passing from Stage 1 (`Candidate`) to Stage 2 (`Ingested Artifact`). Invalid payloads, missing URLs, or non-deterministic coordinates are rejected immediately.
