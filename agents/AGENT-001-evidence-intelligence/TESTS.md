# Test Suite · AGENT-001: Evidence Intelligence

---

## Test Cases

### TC-001: Classify Official Shipyard Blueprint
- **Input**: Chantiers de l'Atlantique General Arrangement PDF for `msc-bellissima`.
- **Expected Output**:
  * `source_type`: `OFFICIAL_SHIPYARD`
  * `relevance_score`: $\ge 0.95$
  * `verification_status`: `VERIFIED`

### TC-002: Reject Travel Blog & Affiliate Links
- **Input**: "CruiseFan123 Top 10 Cabins on Bellissima" promotional blog.
- **Expected Output**:
  * Filtered out in `scan_summary.rejected_promotional` increment.
  * No candidate generated.

### TC-003: Port Authority Harbour Dispatch
- **Input**: Port of Genoa (Ponte dei Mille) Berth 2 Gangway Allocation Notice.
- **Expected Output**:
  * `source_type`: `OFFICIAL_AUTHORITY`
  * `entity_target.entity_type`: `port`
  * `entity_target.slug`: `genoa`
  * `relevance_score`: $\ge 0.90$

### TC-004: Schema Conformance
- **Validation**: Every emitted candidate passes `jsonschema.validate()` against `artifact-candidate.schema.json`.
