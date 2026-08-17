"""
Truth Engine Bridge Connector.
Connects Knowledge Factory candidate evidence to Truth Engine Registered Artifacts.

Contract:
- Input: ArtifactCandidate JSON
- Output: Registered Artifact (conforming to schemas/artifact.schema.json)
- Constraint: No extraction, no statements, no review. Only deterministic registration.
"""

from __future__ import annotations
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class TruthEngineBridge:
    """Deterministic bridge from ArtifactCandidate to Registered Artifact."""

    TRUST_LEVEL_MAP = {
        "OFFICIAL_SHIPYARD": "OFFICIAL",
        "OFFICIAL_AUTHORITY": "OFFICIAL",
        "MARITIME_REGISTRY": "VERIFIED",
        "OPERATOR_TECHNICAL": "VERIFIED",
        "DECK_OFFICER_LOG": "VERIFIED",
    }

    MIME_MAP = {
        "PDF": "application/pdf",
        "JSON": "application/json",
        "HTML": "text/html",
        "IMAGE": "image/jpeg",
        "CAD": "application/octet-stream",
    }

    @classmethod
    def register_candidate(
        cls,
        candidate: Dict[str, Any],
        raw_bytes: Optional[bytes] = None,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Transforms an ArtifactCandidate payload into an immutable Registered Artifact.
        """
        candidate_id = candidate.get("candidate_id", "")
        if not candidate_id:
            raise ValueError("Candidate missing 'candidate_id'")

        # 1. Compute Deterministic SHA-256 Checksum
        extracted = candidate.get("extracted_metadata", {})
        existing_hash = extracted.get("content_hash")

        if raw_bytes is not None:
            sha256 = hashlib.sha256(raw_bytes).hexdigest()
        elif existing_hash and re.match(r"^[a-f0-9]{64}$", existing_hash):
            sha256 = existing_hash.lower()
        else:
            # Fallback deterministic canonical JSON hash of candidate
            canonical_repr = json.dumps(candidate, sort_keys=True).encode("utf-8")
            sha256 = hashlib.sha256(canonical_repr).hexdigest()

        # 2. Derive Unique Artifact ID
        clean_id_suffix = candidate_id.replace("cand-", "")
        artifact_id = f"art-{clean_id_suffix}"

        # 3. Entity & Storage Paths
        target = candidate.get("entity_target", {})
        entity_type = target.get("entity_type", "ship")
        slug = target.get("slug", "unknown")

        fmt = extracted.get("file_format", "JSON").upper()
        ext = fmt.lower() if fmt in ["PDF", "JSON", "HTML"] else "bin"
        storage_path = f"artifacts/{entity_type}/{slug}/{clean_id_suffix}.{ext}"

        mime_type = cls.MIME_MAP.get(fmt, "application/json")

        # 4. Provenance & Authority
        source_type = candidate.get("source_type", "OFFICIAL_SHIPYARD")
        trust_level = cls.TRUST_LEVEL_MAP.get(source_type, "VERIFIED")
        authority = extracted.get("authoritative_publisher") or f"Authority for {slug}"

        # 5. Timestamp
        timestamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 6. Form Registered Artifact Contract
        registered_artifact = {
            "artifact_id": artifact_id,
            "candidate_id": candidate_id,
            "storage_path": storage_path,
            "mime_type": mime_type,
            "sha256": sha256,
            "source_url": candidate.get("source_url", ""),
            "provenance": {
                "source_type": source_type,
                "authority": authority,
                "trust_level": trust_level,
            },
            "ingested_at": timestamp,
        }

        return registered_artifact

    @classmethod
    def process_candidate_file(
        cls,
        file_path: str,
        output_dir: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Reads candidate file (single object or list), registers each artifact,
        and optionally writes out registered artifacts.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = data if isinstance(data, list) else [data]
        registered_list = [cls.register_candidate(c) for c in candidates]

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            for art in registered_list:
                out_path = os.path.join(output_dir, f"{art['artifact_id']}.json")
                with open(out_path, "w", encoding="utf-8") as out_f:
                    json.dump(art, out_f, indent=2, ensure_ascii=False)

        return registered_list


def main():
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
