import unittest
import os
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMAS_DIR = os.path.join(REPO_ROOT, "schemas")
AGENTS_DIR = os.path.join(REPO_ROOT, "agents")
EXAMPLES_DIR = os.path.join(REPO_ROOT, "examples")


class TestKnowledgeFactorySchemas(unittest.TestCase):
    def test_candidate_schema_validity(self):
        """Verify artifact-candidate.schema.json is valid JSON with required Draft-07 properties."""
        schema_path = os.path.join(SCHEMAS_DIR, "artifact-candidate.schema.json")
        self.assertTrue(os.path.exists(schema_path))
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        self.assertEqual(schema.get("$schema"), "http://json-schema.org/draft-07/schema#")
        self.assertIn("properties", schema)
        self.assertIn("candidate_id", schema["properties"])
        self.assertIn("source_type", schema["properties"])

    def test_artifact_schema_validity(self):
        """Verify artifact.schema.json is valid JSON with required Draft-07 properties."""
        schema_path = os.path.join(SCHEMAS_DIR, "artifact.schema.json")
        self.assertTrue(os.path.exists(schema_path))
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        self.assertEqual(schema.get("$schema"), "http://json-schema.org/draft-07/schema#")
        self.assertIn("properties", schema)
        self.assertIn("artifact_id", schema["properties"])
        self.assertIn("sha256", schema["properties"])

    def test_statement_schema_validity(self):
        """Verify statement.schema.json is valid JSON with required Draft-07 properties."""
        schema_path = os.path.join(SCHEMAS_DIR, "statement.schema.json")
        self.assertTrue(os.path.exists(schema_path))
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        self.assertEqual(schema.get("$schema"), "http://json-schema.org/draft-07/schema#")
        self.assertIn("properties", schema)
        self.assertIn("statement_id", schema["properties"])
        self.assertIn("subject_slug", schema["properties"])

    def test_bellissima_candidates_example_conformance(self):
        """Verify examples/bellissima_candidates.json conforms to candidate contract."""
        example_path = os.path.join(EXAMPLES_DIR, "bellissima_candidates.json")
        self.assertTrue(os.path.exists(example_path))
        with open(example_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)

        self.assertIsInstance(candidates, list)
        self.assertGreaterEqual(len(candidates), 2)
        for cand in candidates:
            self.assertTrue(cand["candidate_id"].startswith("cand-"))
            self.assertIn("source_url", cand)
            self.assertIn("source_type", cand)
            self.assertIn("relevance_score", cand)
            self.assertGreaterEqual(cand["relevance_score"], 0.0)
            self.assertLessEqual(cand["relevance_score"], 1.0)
            self.assertIn(cand["verification_status"], ["PENDING", "VERIFIED", "REJECTED"])

    def test_agent_001_directory_completeness(self):
        """Verify AGENT-001 has all required specification files."""
        agent_dir = os.path.join(AGENTS_DIR, "AGENT-001-evidence-intelligence")
        expected_files = ["README.md", "SYSTEM_PROMPT.md", "OUTPUT_SCHEMA.json", "TESTS.md", "CHANGELOG.md"]
        for fname in expected_files:
            fpath = os.path.join(agent_dir, fname)
            self.assertTrue(os.path.exists(fpath), f"Missing {fname} in AGENT-001")

    def test_agent_002_directory_completeness(self):
        """Verify AGENT-002 has all required specification files."""
        agent_dir = os.path.join(AGENTS_DIR, "AGENT-002-artifact-intake")
        expected_files = ["README.md", "SYSTEM_PROMPT.md", "OUTPUT_SCHEMA.json", "TESTS.md", "CHANGELOG.md"]
        for fname in expected_files:
            fpath = os.path.join(agent_dir, fname)
            self.assertTrue(os.path.exists(fpath), f"Missing {fname} in AGENT-002")


if __name__ == "__main__":
    unittest.main()
