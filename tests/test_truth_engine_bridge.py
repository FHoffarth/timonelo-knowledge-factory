import unittest
import os
import json
import re
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.connectors.truth_engine_bridge import TruthEngineBridge


class TestTruthEngineBridgeBoundary(unittest.TestCase):
    """
    Tests enforce the responsibility boundary of the connector.
    The connector must perform only deterministic, mechanical transformations.
    No trust evaluation. No credibility inference.
    """

    def setUp(self):
        examples_dir = os.path.join(REPO_ROOT, "examples")
        with open(os.path.join(examples_dir, "bellissima_candidates.json"), "r", encoding="utf-8") as f:
            self.sample_candidates = json.load(f)

    # ─── Structural correctness ──────────────────────────────────────────────

    def test_artifact_id_is_namespace_swap_of_candidate_id(self):
        """artifact_id is always 'art-' + the suffix from 'cand-'. No logic, no hash."""
        cand = self.sample_candidates[0]
        artifact = TruthEngineBridge.register_candidate(cand)
        self.assertEqual(artifact["artifact_id"], "art-bellissima-ga-2019")
        self.assertEqual(artifact["candidate_id"], "cand-bellissima-ga-2019")

    def test_both_ids_are_present_and_distinct(self):
        """ArtifactCandidate and RegisteredArtifact remain independently addressable."""
        cand = self.sample_candidates[0]
        artifact = TruthEngineBridge.register_candidate(cand)
        self.assertIn("artifact_id", artifact)
        self.assertIn("candidate_id", artifact)
        self.assertNotEqual(artifact["artifact_id"], artifact["candidate_id"])

    def test_storage_path_is_derived_from_entity_coordinates(self):
        """Storage path encodes entity_type and slug from entity_target, nothing more."""
        cand = self.sample_candidates[0]
        artifact = TruthEngineBridge.register_candidate(cand)
        self.assertEqual(
            artifact["storage_path"],
            "artifacts/ship/msc-bellissima/bellissima-ga-2019.pdf"
        )

    def test_mime_type_is_deterministic_format_lookup(self):
        """MIME type is a mechanical format→type mapping, not a quality evaluation."""
        cand = self.sample_candidates[0]  # file_format: PDF
        artifact = TruthEngineBridge.register_candidate(cand)
        self.assertEqual(artifact["mime_type"], "application/pdf")

        cand2 = self.sample_candidates[1]  # file_format: JSON
        artifact2 = TruthEngineBridge.register_candidate(cand2)
        self.assertEqual(artifact2["mime_type"], "application/json")

    def test_sha256_computed_from_raw_bytes(self):
        """SHA-256 is the hash of the actual bytes, deterministic and reproducible."""
        cand = self.sample_candidates[0]
        raw = b"PDF-1.7 Naval Architecture General Arrangement MSC Bellissima"
        artifact = TruthEngineBridge.register_candidate(cand, raw_bytes=raw)
        expected = "2290c639a1ee61e338137df3eea5ed174331cae0f3430f7f5c77d26fe0ff3301"
        self.assertEqual(artifact["sha256"], expected)
        self.assertTrue(re.match(r"^[a-f0-9]{64}$", artifact["sha256"]))

    def test_sha256_falls_through_to_existing_hash(self):
        """Existing 64-char hex hash is preserved verbatim when no raw bytes given."""
        cand = self.sample_candidates[0]
        artifact = TruthEngineBridge.register_candidate(cand)
        # The candidate carries a valid 64-char hex hash — connector must pass it through.
        expected = cand["extracted_metadata"]["content_hash"]
        self.assertEqual(artifact["sha256"], expected)

    def test_source_url_is_preserved_verbatim(self):
        """source_url is copied from the candidate without modification."""
        cand = self.sample_candidates[0]
        artifact = TruthEngineBridge.register_candidate(cand)
        self.assertEqual(artifact["source_url"], cand["source_url"])

    def test_timestamp_is_assigned_at_ingestion(self):
        """ingested_at is an ISO 8601 UTC timestamp from the moment of registration."""
        cand = self.sample_candidates[0]
        fixed = datetime(2026, 8, 17, 12, 0, 0, tzinfo=timezone.utc)
        artifact = TruthEngineBridge.register_candidate(cand, now=fixed)
        self.assertEqual(artifact["ingested_at"], "2026-08-17T12:00:00Z")

    # ─── Responsibility boundary: NO TRUST ───────────────────────────────────

    def test_connector_does_not_produce_trust_level(self):
        """
        BOUNDARY: trust_level must NOT appear in connector output.
        Trust evaluation belongs to the Truth Engine.
        """
        for cand in self.sample_candidates:
            artifact = TruthEngineBridge.register_candidate(cand)
            prov = artifact.get("provenance", {})
            self.assertNotIn(
                "trust_level", prov,
                msg=f"Connector must not derive trust_level. Found in provenance for {cand['candidate_id']}"
            )

    def test_connector_does_not_produce_authority_level(self):
        """BOUNDARY: authority_level must NOT appear in connector output."""
        for cand in self.sample_candidates:
            artifact = TruthEngineBridge.register_candidate(cand)
            prov = artifact.get("provenance", {})
            self.assertNotIn("authority_level", prov)

    def test_connector_does_not_synthesize_authority_string(self):
        """
        BOUNDARY: connector must not fabricate an authority string when publisher is missing.
        If authoritative_publisher is absent in the candidate, provenance must omit the field.
        """
        cand_no_publisher = {
            "candidate_id": "cand-test-no-publisher",
            "source_url": "https://example.com/doc.pdf",
            "source_type": "OPERATOR_TECHNICAL",
            "title": "Test without publisher",
            "discovered_at": "2026-08-17T00:00:00Z",
            "entity_target": {"entity_type": "ship", "slug": "test-vessel"},
            "relevance_score": 0.75,
            "verification_status": "PENDING",
            "extracted_metadata": {"file_format": "PDF"}
        }
        artifact = TruthEngineBridge.register_candidate(cand_no_publisher)
        prov = artifact["provenance"]
        self.assertNotIn(
            "authoritative_publisher", prov,
            msg="Connector must not synthesize a publisher when none is declared in the candidate."
        )

    def test_source_type_is_preserved_verbatim_not_evaluated(self):
        """
        BOUNDARY: source_type is passed through unchanged.
        The connector must not use it as a trigger for credibility inference.
        """
        for cand in self.sample_candidates:
            artifact = TruthEngineBridge.register_candidate(cand)
            self.assertEqual(artifact["provenance"]["source_type"], cand["source_type"])

    def test_authoritative_publisher_is_preserved_when_present(self):
        """Connector preserves authoritative_publisher verbatim when declared."""
        cand = self.sample_candidates[0]
        artifact = TruthEngineBridge.register_candidate(cand)
        self.assertEqual(
            artifact["provenance"]["authoritative_publisher"],
            "Chantiers de l'Atlantique"
        )

    # ─── Immutability ─────────────────────────────────────────────────────────

    def test_candidate_is_not_mutated(self):
        """ArtifactCandidate must not be modified during registration."""
        cand = self.sample_candidates[0]
        original = json.loads(json.dumps(cand))
        TruthEngineBridge.register_candidate(cand)
        self.assertEqual(cand, original)

    # ─── Batch processing ────────────────────────────────────────────────────

    def test_batch_file_processing(self):
        """Verify batch registration returns one artifact per candidate."""
        candidates_path = os.path.join(REPO_ROOT, "examples", "bellissima_candidates.json")
        artifacts = TruthEngineBridge.process_candidate_file(candidates_path)
        self.assertEqual(len(artifacts), 2)
        for art in artifacts:
            self.assertTrue(art["artifact_id"].startswith("art-"))
            self.assertTrue(art["candidate_id"].startswith("cand-"))

    def test_missing_candidate_id_raises(self):
        """Connector must reject candidates without a candidate_id."""
        with self.assertRaises(ValueError):
            TruthEngineBridge.register_candidate({"source_url": "https://example.com/doc.pdf"})


if __name__ == "__main__":
    unittest.main()
