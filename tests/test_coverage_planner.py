import unittest
import os
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.agents.coverage_planner import CoveragePlanner


# ─── Shared Fixtures ─────────────────────────────────────────────────────────

def make_request(
    answered: int,
    unknowns: list[dict],
    authority_matrix: list[dict],
    entity_slug: str = "msc-bellissima",
) -> dict:
    return {
        "entity_slug": entity_slug,
        "statement_inventory": {
            "answered": answered,
            "unknown": len(unknowns),
        },
        "unknown_register": unknowns,
        "authority_matrix": authority_matrix,
    }


UNKNOWNS_BELLISSIMA = [
    {"predicate": "deck_14_cabin_count",       "subject_slug": "msc-bellissima"},
    {"predicate": "deck_14_elevator_distance", "subject_slug": "msc-bellissima"},
    {"predicate": "muster_station_deck",       "subject_slug": "msc-bellissima"},
    {"predicate": "step_free_gangway_deck",    "subject_slug": "msc-bellissima"},
    {"predicate": "noise_class_deck_15",       "subject_slug": "msc-bellissima"},
    {"predicate": "noise_class_deck_13",       "subject_slug": "msc-bellissima"},
    {"predicate": "ada_bathroom_count",        "subject_slug": "msc-bellissima"},
    {"predicate": "ada_route_to_lift",         "subject_slug": "msc-bellissima"},
    {"predicate": "gangway_port_genoa",        "subject_slug": "genoa"},
    {"predicate": "gangway_port_barcelona",    "subject_slug": "barcelona"},
]

AUTHORITY_MATRIX = [
    {
        "document_class": "General Arrangement Drawing",
        "addressable_predicates": [
            "deck_14_cabin_count",
            "deck_14_elevator_distance",
            "step_free_gangway_deck",
            "noise_class_deck_15",
            "noise_class_deck_13",
        ],
    },
    {
        "document_class": "Accessibility Guide",
        "addressable_predicates": [
            "ada_bathroom_count",
            "ada_route_to_lift",
            "step_free_gangway_deck",
        ],
    },
    {
        "document_class": "Safety Management Plan",
        "addressable_predicates": [
            "muster_station_deck",
        ],
    },
    {
        "document_class": "Port Authority Berth Notice",
        "addressable_predicates": [
            "gangway_port_genoa",
            "gangway_port_barcelona",
        ],
    },
]

FIXED_TIME = datetime(2026, 8, 17, 18, 0, 0, tzinfo=timezone.utc)


class TestCoveragePlannerCore(unittest.TestCase):

    # ─── Coverage computation ─────────────────────────────────────────────────

    def test_coverage_percent_53_percent(self):
        """Verified: 418 answered + 374 unknown = 53% coverage."""
        request = make_request(
            answered=418,
            unknowns=[{"predicate": "x", "subject_slug": "s"}] * 374,
            authority_matrix=[{
                "document_class": "General Arrangement Drawing",
                "addressable_predicates": ["x"],
            }],
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(plan["coverage"]["answered"], 418)
        self.assertEqual(plan["coverage"]["unknown"], 374)
        self.assertEqual(plan["coverage"]["coverage_percent"], 52.8)

    def test_coverage_percent_zero_answered(self):
        """Edge: 0 answered statements produces 0.0% coverage."""
        request = make_request(
            answered=0,
            unknowns=[{"predicate": "x", "subject_slug": "s"}],
            authority_matrix=[{
                "document_class": "Doc",
                "addressable_predicates": ["x"],
            }],
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(plan["coverage"]["coverage_percent"], 0.0)

    def test_coverage_percent_fully_answered(self):
        """Edge: 0 unknowns produces 100.0% coverage."""
        request = make_request(
            answered=200,
            unknowns=[],
            authority_matrix=[{
                "document_class": "Doc",
                "addressable_predicates": ["x"],
            }],
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(plan["coverage"]["coverage_percent"], 100.0)

    # ─── Priority ranking ─────────────────────────────────────────────────────

    def test_highest_gain_document_class_is_recommended(self):
        """
        Given 10 unknowns and the authority matrix above,
        General Arrangement Drawing covers 5 unknowns — more than any other class.
        It must be ranked first.
        """
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(
            plan["recommended_next_document"]["document_class"],
            "General Arrangement Drawing",
        )
        self.assertEqual(
            plan["recommended_next_document"]["expected_new_statements"], 5
        )

    def test_roadmap_is_sorted_by_expected_gain_descending(self):
        """Roadmap priorities must strictly follow descending expected_new_statements."""
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        gains = [entry["expected_new_statements"] for entry in plan["roadmap"]]
        self.assertEqual(gains, sorted(gains, reverse=True))

    def test_roadmap_priorities_are_sequential(self):
        """Priority field must be 1, 2, 3, … without gaps."""
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        priorities = [entry["priority"] for entry in plan["roadmap"]]
        self.assertEqual(priorities, list(range(1, len(priorities) + 1)))

    def test_roadmap_contains_all_authority_matrix_entries(self):
        """Every document class in the authority matrix must appear in the roadmap."""
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        roadmap_classes = {entry["document_class"] for entry in plan["roadmap"]}
        matrix_classes = {entry["document_class"] for entry in AUTHORITY_MATRIX}
        self.assertEqual(roadmap_classes, matrix_classes)

    def test_document_class_with_no_matching_unknowns_scores_zero(self):
        """
        A document class whose predicates do not overlap with any unknown predicate
        must still appear in the roadmap with expected_new_statements = 0.
        """
        request = make_request(
            answered=100,
            unknowns=[{"predicate": "deck_14_cabin_count", "subject_slug": "msc-bellissima"}],
            authority_matrix=[
                {
                    "document_class": "General Arrangement Drawing",
                    "addressable_predicates": ["deck_14_cabin_count"],
                },
                {
                    "document_class": "Completely Irrelevant Doc",
                    "addressable_predicates": ["some_other_predicate"],
                },
            ],
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        irrelevant = next(
            e for e in plan["roadmap"] if e["document_class"] == "Completely Irrelevant Doc"
        )
        self.assertEqual(irrelevant["expected_new_statements"], 0)
        self.assertEqual(irrelevant["expected_unknown_reduction_percent"], 0.0)

    def test_tie_breaking_is_alphabetical_by_document_class(self):
        """
        When two document classes yield identical gain, they must be ordered
        alphabetically for deterministic output.
        """
        request = make_request(
            answered=10,
            unknowns=[
                {"predicate": "pred_a", "subject_slug": "s"},
                {"predicate": "pred_b", "subject_slug": "s"},
            ],
            authority_matrix=[
                {"document_class": "Zebra Doc", "addressable_predicates": ["pred_a"]},
                {"document_class": "Alpha Doc", "addressable_predicates": ["pred_b"]},
            ],
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(plan["roadmap"][0]["document_class"], "Alpha Doc")
        self.assertEqual(plan["roadmap"][1]["document_class"], "Zebra Doc")

    # ─── Output contract ─────────────────────────────────────────────────────

    def test_output_has_all_required_fields(self):
        """Plan output must contain all required top-level fields."""
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        for field in ("entity_slug", "computed_at", "coverage",
                      "recommended_next_document", "roadmap"):
            self.assertIn(field, plan)

    def test_entity_slug_is_preserved_in_output(self):
        """entity_slug from request must appear unchanged in output."""
        request = make_request(
            answered=100,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
            entity_slug="ms-andorinha",
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(plan["entity_slug"], "ms-andorinha")

    def test_computed_at_is_fixed_when_now_is_supplied(self):
        """Timestamp must equal the injected 'now' for deterministic testing."""
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(plan["computed_at"], "2026-08-17T18:00:00Z")

    def test_recommended_next_matches_roadmap_priority_1(self):
        """recommended_next_document must always equal roadmap[0]."""
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        top = plan["roadmap"][0]
        rec = plan["recommended_next_document"]
        self.assertEqual(rec["document_class"], top["document_class"])
        self.assertEqual(rec["expected_new_statements"], top["expected_new_statements"])

    # ─── Responsibility boundary ─────────────────────────────────────────────

    def test_planner_does_not_produce_trust_fields(self):
        """BOUNDARY: planner output must contain no trust, credibility, or authority fields."""
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        plan = CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        forbidden_fields = {"trust_level", "authority_level", "verified_truth", "ground_truth"}
        all_keys = set(plan.keys()) | set(plan.get("coverage", {}).keys())
        self.assertTrue(
            forbidden_fields.isdisjoint(all_keys),
            f"Planner output must not contain trust fields. Found: {forbidden_fields & all_keys}",
        )

    def test_planner_does_not_modify_request(self):
        """BOUNDARY: the input request must not be mutated by the planner."""
        import json as _json
        request = make_request(
            answered=418,
            unknowns=UNKNOWNS_BELLISSIMA,
            authority_matrix=AUTHORITY_MATRIX,
        )
        original = _json.loads(_json.dumps(request))
        CoveragePlanner().compute_plan(request, now=FIXED_TIME)
        self.assertEqual(request, original)

    # ─── Error handling ───────────────────────────────────────────────────────

    def test_empty_authority_matrix_raises(self):
        """Planner must raise when the authority matrix is empty."""
        request = {
            "entity_slug": "msc-bellissima",
            "statement_inventory": {"answered": 10, "unknown": 5},
            "unknown_register": [{"predicate": "x", "subject_slug": "s"}],
            "authority_matrix": [],
        }
        with self.assertRaises((ValueError, IndexError)):
            CoveragePlanner().compute_plan(request, now=FIXED_TIME)


if __name__ == "__main__":
    unittest.main()
