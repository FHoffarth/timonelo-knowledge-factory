# Test Suite · AGENT-002: Artifact Intake

---

## Test Cases

### TC-101: Ingest Shipyard PDF with SHA-256
- **Input**: Valid `ArtifactCandidate` referencing MSC Bellissima GA blueprint.
- **Expected Output**:
  * Emits `IngestedArtifact` with valid `sha256` pattern (`^[a-f0-9]{64}$`).
  * `storage_path`: `artifacts/ship/msc-bellissima/cand-bellissima-ga-2019.pdf`.
  * `status`: `INGESTED_NEW`.

### TC-102: Duplicate Hash Detection
- **Input**: Re-ingestion of same byte stream.
- **Expected Output**:
  * `status`: `UPDATED_EXISTING`.
  * Preserves original `artifact_id`.

### TC-103: Schema Conformance
- **Validation**: Generated artifacts strictly pass `artifact.schema.json`.
