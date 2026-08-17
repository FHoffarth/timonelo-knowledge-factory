import unittest
import os
import json
import re
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.connectors.truth_engine_bridge import TruthEngineBridge


class TestTruthEngineBridge(unittest.TestCase):
    def setUp(self):
        self.schemas_dir = os.path.join(REPO_ROOT, "schemas")
        self.examples_dir = os.path.join(REPO_ROOT, "examples")

        with open(os.path.join(self.schemas_dir, "artifact.schema.json"), "r", encoding="utf-8") as f:
            self.artifact_schema = json.load(f)

        with open(os.path.join(self.examples_dir, "bellissima_candidates.json"), "r", encoding="utf-8") as f:
            self.sample_candidates = json.load(f)

    def test_single_candidate_registration(self):
        """Verify registering a candidate produces a valid Registered Artifact contract."""
        cand = self.sample_candidates[0]
        fixed_time = datetime(2026, 8, 17, 12, 0, 0, tzinfo=timezone.utc)
        
        artifact = TruthEngineBridge.register_candidate(cand, now=fixed_time)

        # 1. Required fields
        self.assertEqual(artifact["artifact_id"], "art-bellissima-ga-2019")
        self.assertEqual(artifact["candidate_id"], "cand-bellissima-ga-2019")
        self.assertEqual(artifact["storage_path"], "artifacts/ship/msc-bellissima/bellissima-ga-2019.pdf")
        self.assertEqual(artifact["mime_type"], "application/pdf")
        self.assertTrue(re.match(r"^[a-f0-9]{64}$", artifact["sha256"]))
        self.assertEqual(artifact["source_url"], cand["source_url"])
        self.assertEqual(artifact["ingested_at"], "2026-08-17T12:00:00Z")

        # 2. Provenance
        prov = artifact["provenance"]
        self.assertEqual(prov["source_type"], "OFFICIAL_SHIPYARD")
        self.assertEqual(prov["authority"], "Chantiers de l'Atlantique")
        self.assertEqual(prov["trust_level"], "OFFICIAL")

    def test_authority_port_candidate_registration(self):
        """Verify registering a port authority candidate maps trust level to OFFICIAL."""
        cand = self.sample_candidates[1]
        artifact = TruthEngineBridge.register_candidate(cand)

        self.assertEqual(artifact["artifact_id"], "art-genoa-ponte-mille-2026")
        self.assertEqual(artifact["storage_path"], "artifacts/port/genoa/genoa-ponte-mille-2026.json")
        self.assertEqual(artifact["mime_type"], "application/json")
        self.assertEqual(artifact["provenance"]["trust_level"], "OFFICIAL")

    def test_sha256_computation_from_raw_bytes(self):
        """Verify SHA-256 hash is computed deterministically when raw bytes are passed."""
        cand = self.sample_candidates[0]
        dummy_content = b"PDF-1.7 Naval Architecture General Arrangement MSC Bellissima"
        
        artifact = TruthEngineBridge.register_candidate(cand, raw_bytes=dummy_content)
        expected_hash = "2290c639a1ee61e338137df3eea5ed174331cae0f3430f7f5c77d26fe0ff3301"
        self.assertEqual(artifact["sha256"], expected_hash)

    def test_batch_file_processing(self):
        """Verify processing the entire examples file."""
        candidates_path = os.path.join(self.examples_dir, "bellissima_candidates.json")
        artifacts = TruthEngineBridge.process_candidate_file(candidates_path)

        self.assertEqual(len(artifacts), 2)
        self.assertTrue(artifacts[0]["artifact_id"].startswith("art-"))
        self.assertTrue(artifacts[1]["artifact_id"].startswith("art-"))


if __name__ == "__main__":
    unittest.main()
