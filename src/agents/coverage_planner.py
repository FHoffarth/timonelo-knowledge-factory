"""
src/agents/coverage_planner.py

AGENT-003: Coverage Planner
===========================

Responsibility boundary:
    Plans evidence acquisition. Nothing else.

Permitted:
    - Compute statement coverage from inventory
    - Identify UNKNOWN statements from the unknown register
    - Map unknown predicates to document classes via authority matrix
    - Count expected knowledge gain per document class
    - Rank document classes by expected gain
    - Produce an Evidence Acquisition Plan

Forbidden:
    - Search the internet
    - Download documents
    - Assign trust
    - Create statements
    - Answer passenger questions
    - Override the Truth Engine

Input:  CoveragePlanRequest  (schemas/coverage-plan-request.schema.json)
Output: EvidenceAcquisitionPlan (schemas/evidence-acquisition-plan.schema.json)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ─── Data Structures ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class UnknownStatement:
    predicate: str
    subject_slug: str


@dataclass(frozen=True)
class AuthorityEntry:
    document_class: str
    addressable_predicates: frozenset[str]


@dataclass(frozen=True)
class DocumentClassGain:
    document_class: str
    expected_new_statements: int
    expected_unknown_reduction_percent: float


# ─── Planner ─────────────────────────────────────────────────────────────────

class CoveragePlanner:
    """
    Deterministic Evidence Acquisition Planner.

    Given the current statement inventory, unknown register, and authority matrix,
    computes which document class should be acquired next to maximise truthful
    knowledge growth.

    This class performs NO truth evaluation, NO trust assignment, NO document retrieval.
    """

    def compute_plan(
        self,
        request: dict[str, Any],
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Core planning method.

        Args:
            request: A dict conforming to coverage-plan-request.schema.json.
            now:     Optional datetime override for deterministic testing.

        Returns:
            A dict conforming to evidence-acquisition-plan.schema.json.
        """
        entity_slug: str = request["entity_slug"]
        inventory: dict[str, int] = request["statement_inventory"]
        answered: int = inventory["answered"]
        unknown_count: int = inventory["unknown"]
        total: int = answered + unknown_count

        # 1. Coverage calculation
        coverage_percent: float = (
            round((answered / total) * 100, 1) if total > 0 else 0.0
        )

        # 2. Parse unknown register
        unknowns: list[UnknownStatement] = [
            UnknownStatement(
                predicate=u["predicate"],
                subject_slug=u["subject_slug"],
            )
            for u in request.get("unknown_register", [])
        ]
        unknown_predicates: set[str] = {u.predicate for u in unknowns}

        # 3. Parse authority matrix
        authority: list[AuthorityEntry] = [
            AuthorityEntry(
                document_class=entry["document_class"],
                addressable_predicates=frozenset(entry["addressable_predicates"]),
            )
            for entry in request["authority_matrix"]
        ]

        # 4. Compute expected knowledge gain per document class.
        #    Gain = number of distinct unknown predicates covered by this document class.
        #    Reduction = gain / total_unknowns * 100.
        gains: list[DocumentClassGain] = []
        for entry in authority:
            covered_predicates = entry.addressable_predicates & unknown_predicates
            # Count individual unknown statements (not just predicates) that would be resolved.
            # A statement is resolved if its predicate is covered by this document class.
            new_statements = sum(
                1 for u in unknowns if u.predicate in covered_predicates
            )
            reduction = (
                round((new_statements / unknown_count) * 100, 1)
                if unknown_count > 0
                else 0.0
            )
            gains.append(DocumentClassGain(
                document_class=entry.document_class,
                expected_new_statements=new_statements,
                expected_unknown_reduction_percent=reduction,
            ))

        # 5. Rank by expected_new_statements descending, then document_class alphabetically
        #    for deterministic tie-breaking.
        ranked: list[DocumentClassGain] = sorted(
            gains,
            key=lambda g: (-g.expected_new_statements, g.document_class),
        )

        # 6. Guard: if nothing can be planned (all unknowns have no matching document class)
        if not ranked:
            raise ValueError(
                "Authority matrix is empty — cannot produce an acquisition plan."
            )

        top = ranked[0]
        timestamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "entity_slug": entity_slug,
            "computed_at": timestamp,
            "coverage": {
                "answered": answered,
                "unknown": unknown_count,
                "coverage_percent": coverage_percent,
            },
            "recommended_next_document": {
                "document_class": top.document_class,
                "expected_new_statements": top.expected_new_statements,
                "expected_unknown_reduction_percent": top.expected_unknown_reduction_percent,
            },
            "roadmap": [
                {
                    "priority": i + 1,
                    "document_class": g.document_class,
                    "expected_new_statements": g.expected_new_statements,
                    "expected_unknown_reduction_percent": g.expected_unknown_reduction_percent,
                }
                for i, g in enumerate(ranked)
            ],
        }

    @classmethod
    def from_file(
        cls,
        request_path: str,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Reads a CoveragePlanRequest JSON file, computes the plan, and optionally
        writes the EvidenceAcquisitionPlan to output_path.
        """
        with open(request_path, "r", encoding="utf-8") as f:
            request = json.load(f)

        plan = cls().compute_plan(request)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(plan, f_out, indent=2, ensure_ascii=False)

        return plan


def main() -> None:
    import sys
    if len(sys.argv) < 2:
        print("Usage: python coverage_planner.py <request_json> [output_json]")
        sys.exit(1)

    request_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    plan = CoveragePlanner.from_file(request_path, output_path)
    print(json.dumps(plan, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
