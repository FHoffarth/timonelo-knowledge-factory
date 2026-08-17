# AGENT-002: Artifact Intake Agent

> **Normalization, Storage Ingestion, and Cryptographic Hash Validation of Maritime Evidence.**

---

## 1. Mission
The Artifact Intake Agent ingests candidate evidence passed from `AGENT-001`, computes SHA-256 integrity checksums, extracts structured text sections, and stores immutable artifact copies conforming to [`schemas/artifact.schema.json`](../../schemas/artifact.schema.json).

---

## 2. Responsibilities
- **Integrity Verification**: Calculate cryptographic SHA-256 hash of downloaded PDFs, CAD plans, or JSON telemetries.
- **Section Parsing**: Segment multi-deck General Arrangements into discrete deck levels and coordinate zones.
- **Storage Management**: Store artifacts into immutable, versioned directories (`artifacts/{entity_type}/{slug}/`).
- **Provenance Sealing**: Attach immutable author, source URL, and timestamp records.

---

## 3. Forbidden Actions
- ❌ **NEVER modify original binary bytes**: Artifacts must remain byte-for-byte identical to shipyard source releases.
- ❌ **NEVER bypass hash collision checks**: If a file hash matches an existing artifact, update provenance without duplicate storage.

---

## 4. Input Contract
Consumes validated `ArtifactCandidate` payloads from `AGENT-001`.

---

## 5. Output Contract
Emits an `IngestedArtifact` conforming strictly to [`schemas/artifact.schema.json`](../../schemas/artifact.schema.json).
