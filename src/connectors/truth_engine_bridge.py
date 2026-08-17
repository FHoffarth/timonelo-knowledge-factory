"""
Truth Engine Connector Bridge.

Responsibility boundary:
  - This module performs ONLY deterministic, mechanical transformations.
  - It MUST NOT evaluate trust, assign credibility, or derive authority scores.
  - Trust evaluation belongs exclusively to the Truth Engine.

Contract:
  Input:  ArtifactCandidate (conforms to schemas/artifact-candidate.schema.json)
  Output: RegisteredArtifact (conforms to schemas/artifact.schema.json)

Permitted operations:
  - generate artifact_id from candidate_id
  - compute SHA-256 checksum of raw bytes or existing hash
  - map file_format to MIME type
  - derive storage path from entity_type and slug
  - assign ingestion timestamp
  - preserve provenance fields verbatim (source_type, authoritative_publisher)

Forbidden operations:
  - assign trust_level
  - assign authority_level
  - evaluate verified_truth or ground_truth
  - synthesize or infer publisher authority
  - derive credibility from source_type
"""

from __future__ import annotations
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# Deterministic MIME type lookup from file format strings.
# This is a format mapping, not a trust or quality evaluation.
_MIME_MAP: Dict[str, str] = {
    "PDF":  "application/pdf",
    "JSON": "application/json",
    "HTML": "text/html",
    "IMAGE": "image/jpeg",
    "CAD":  "application/octet-stream",
}


class TruthEngineBridge:
    """
    Deterministic connector from ArtifactCandidate to RegisteredArtifact.

    All transformations are mechanical and fully reproducible given the same inputs.
    No trust evaluation. No credibility inference. No opinion.
    """

    @classmethod
    def register_candidate(
        cls,
        candidate: Dict[str, Any],
        raw_bytes: Optional[bytes] = None,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Transforms an ArtifactCandidate into a RegisteredArtifact.

        The ArtifactCandidate is never mutated. Both objects remain independently
        addressable via their respective IDs.
        """
        candidate_id: str = candidate.get("candidate_id", "")
        if not candidate_id:
            raise ValueError("Candidate missing required field 'candidate_id'")

        extracted: Dict[str, Any] = candidate.get("extracted_metadata", {})

        # 1. SHA-256 — deterministic file integrity checksum.
        #    Precedence: raw bytes → existing 64-char hex hash → canonical JSON fingerprint.
        existing_hash: str = extracted.get("content_hash", "")
        if raw_bytes is not None:
            sha256 = hashlib.sha256(raw_bytes).hexdigest()
        elif re.match(r"^[a-f0-9]{64}$", existing_hash):
            sha256 = existing_hash.lower()
        else:
            canonical = json.dumps(candidate, sort_keys=True).encode("utf-8")
            sha256 = hashlib.sha256(canonical).hexdigest()

        # 2. Artifact ID — deterministic namespace swap: cand- → art-.
        id_suffix = candidate_id.removeprefix("cand-")
        artifact_id = f"art-{id_suffix}"

        # 3. Storage path — derived purely from entity coordinates and format.
        target: Dict[str, Any] = candidate.get("entity_target", {})
        entity_type: str = target.get("entity_type", "unknown")
        slug: str = target.get("slug", "unknown")
        fmt: str = extracted.get("file_format", "JSON").upper()
        ext: str = fmt.lower() if fmt in ("PDF", "JSON", "HTML") else "bin"
        storage_path = f"artifacts/{entity_type}/{slug}/{id_suffix}.{ext}"

        # 4. MIME type — mechanical format-to-type lookup table.
        mime_type = _MIME_MAP.get(fmt, "application/octet-stream")

        # 5. Provenance — verbatim passthrough. No derivation, no inference.
        #    source_type: preserved exactly as declared by AGENT-001.
        #    authoritative_publisher: preserved only if present; never synthesized.
        provenance: Dict[str, Any] = {
            "source_type": candidate.get("source_type", ""),
        }
        publisher: str = extracted.get("authoritative_publisher", "")
        if publisher:
            provenance["authoritative_publisher"] = publisher

        # 6. Timestamp — wall-clock moment of connector ingestion.
        ingested_at = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "artifact_id":    artifact_id,
            "candidate_id":   candidate_id,
            "storage_path":   storage_path,
            "mime_type":      mime_type,
            "sha256":         sha256,
            "source_url":     candidate.get("source_url", ""),
            "provenance":     provenance,
            "ingested_at":    ingested_at,
        }

    @classmethod
    def process_candidate_file(
        cls,
        file_path: str,
        output_dir: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Reads a candidate file (single object or list) and registers each artifact.
        Optionally writes output JSON files to output_dir.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = data if isinstance(data, list) else [data]
        registered = [cls.register_candidate(c) for c in candidates]

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            for art in registered:
                out_path = os.path.join(output_dir, f"{art['artifact_id']}.json")
                with open(out_path, "w", encoding="utf-8") as f_out:
                    json.dump(art, f_out, indent=2, ensure_ascii=False)

        return registered


def main() -> None:
    import sys
    if len(sys.argv) < 2:
        print("Usage: python truth_engine_bridge.py <candidate_json_file> [output_dir]")
        sys.exit(1)

    candidate_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    results = TruthEngineBridge.process_candidate_file(candidate_file, output_dir)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
