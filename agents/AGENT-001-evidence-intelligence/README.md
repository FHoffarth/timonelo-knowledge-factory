# AGENT-001: Evidence Intelligence Agent

> **Autonomous Discovery, Classification, and Ranking of Authoritative Maritime Sources.**

---

## 1. Mission
The Evidence Intelligence Agent scans, identifies, filters, and ranks primary maritime documentation (shipyard general arrangements, IMO classification dossiers, port authority notices, and UN/LOCODE terminal directories). It separates authoritative architectural evidence from commercial promotional marketing.

---

## 2. Responsibilities
- **Source Discovery**: Continuously monitor official maritime registers (IMO, GISIS, UN/LOCODE, Chantiers de l'Atlantique, Fincantieri, Meyer Werft).
- **Evidence Grading**: Assign confidence scores based on the Timonelo Evidence Classification Hierarchy.
- **Candidate Generation**: Output schema-validated `ArtifactCandidate` records ready for intake by `AGENT-002`.
- **Negative Intelligence Flagging**: Identify contradictory reports, obsolete berth allocations, and drydock modifications.

---

## 3. Forbidden Actions
- ❌ **NEVER invent certainty**: If an official blueprint is missing, mark the status as `PENDING` with score $< 0.5$.
- ❌ **NEVER ingest promotional or affiliate blogs**: Exclude third-party travel agent marketing without verifiable naval technical backing.
- ❌ **NEVER alter shipyard coordinate dimensions**: Numerical length, beam, and gross tonnage must remain strictly exact to the millimetre/meter.

---

## 4. Input Contract
```json
{
  "target_entity": {
    "entity_type": "ship",
    "slug": "msc-bellissima"
  },
  "search_domains": ["shipyard", "imo", "port_authority"],
  "min_relevance_threshold": 0.70
}
```

---

## 5. Output Contract
Emits an array of `ArtifactCandidate` objects conforming strictly to [`schemas/artifact-candidate.schema.json`](../../schemas/artifact-candidate.schema.json).

---

## 6. Files in this Module
- [`SYSTEM_PROMPT.md`](./SYSTEM_PROMPT.md) - Exact system instructions for the LLM runtime.
- [`OUTPUT_SCHEMA.json`](./OUTPUT_SCHEMA.json) - Dedicated output schema copy.
- [`TESTS.md`](./TESTS.md) - Deterministic evaluation suite.
- [`CHANGELOG.md`](./CHANGELOG.md) - Version history.
