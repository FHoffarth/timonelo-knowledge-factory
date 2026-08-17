# Test Suite · AGENT-003: Coverage Planner

All tests must be deterministic. No external calls. No filesystem side-effects.

---

## TC-301: Standard Coverage Computation at 53%

**Input**  
- `answered`: 418  
- `unknown`: 374  
- Authority matrix: any non-empty

**Expected**  
- `coverage.coverage_percent` = `52.8`  
- `coverage.answered` = `418`  
- `coverage.unknown` = `374`

---

## TC-302: General Arrangement Drawing Ranked First

**Input**  
- 10 unknown statements (deck dimensions, elevator distances, acoustic classifications, gangway decks)  
- Authority matrix:
  - `General Arrangement Drawing` → 5 addressable predicates
  - `Accessibility Guide` → 3 addressable predicates
  - `Safety Management Plan` → 1 addressable predicate
  - `Port Authority Berth Notice` → 2 addressable predicates

**Expected**  
- `recommended_next_document.document_class` = `"General Arrangement Drawing"`  
- `recommended_next_document.expected_new_statements` = `5`  
- Roadmap[0].priority = 1, Roadmap[0].document_class = `"General Arrangement Drawing"`

---

## TC-303: Tie-Breaking Is Alphabetical

**Input**  
- 2 unknown statements with disjoint predicates  
- Authority matrix:
  - `Zebra Doc` → covers predicate_a (1 unknown)  
  - `Alpha Doc` → covers predicate_b (1 unknown)

**Expected**  
- `recommended_next_document.document_class` = `"Alpha Doc"`  
- Roadmap order: `Alpha Doc` then `Zebra Doc`

---

## TC-304: Zero-Gain Document Class Still Appears in Roadmap

**Input**  
- 1 unknown statement with predicate `deck_14_cabin_count`  
- Authority matrix:
  - `General Arrangement Drawing` → `["deck_14_cabin_count"]`  
  - `Irrelevant Doc` → `["some_unrelated_predicate"]`

**Expected**  
- Roadmap contains both entries  
- `Irrelevant Doc`: `expected_new_statements` = 0, `expected_unknown_reduction_percent` = 0.0

---

## TC-305: Zero Answered → 0.0% Coverage

**Input**: `answered = 0`, any unknowns  
**Expected**: `coverage_percent = 0.0`

---

## TC-306: Zero Unknowns → 100.0% Coverage

**Input**: `unknown_register = []`, `answered = 200`  
**Expected**: `coverage_percent = 100.0`

---

## TC-307: Output Contract Conformance

**Input**: Any valid request  
**Expected**: Output matches `evidence-acquisition-plan.schema.json` exactly.

- No `trust_level` field anywhere in output.
- No `authority_level` field anywhere in output.
- `roadmap` priorities are sequential integers starting at 1.
- `recommended_next_document` equals `roadmap[0]`.

---

## TC-308: Input Immutability

**Input**: Any valid request object  
**Expected**: After `compute_plan()`, the input dict is byte-for-byte identical to before.

---

## TC-309: Empty Authority Matrix Raises

**Input**: `authority_matrix = []`  
**Expected**: `ValueError` or `IndexError` — no partial plan emitted.

---

## TC-310: Sequential Priority Field

**Input**: Any 4-entry authority matrix  
**Expected**: Roadmap priorities are `[1, 2, 3, 4]` with no gaps.
