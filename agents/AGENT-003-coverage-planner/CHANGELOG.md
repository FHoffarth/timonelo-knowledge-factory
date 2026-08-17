# Changelog · AGENT-003: Coverage Planner

---

## [1.0.0] — 2026-08-17

### Added
- Initial specification: Mission, Responsibilities, and Forbidden Actions.
- Input schema: `coverage-plan-request.schema.json`.
- Output schema: `evidence-acquisition-plan.schema.json`.
- Dedicated `OUTPUT_SCHEMA.json` in agent module.
- System Prompt specifying deterministic computation algorithm.
- Test suite: 10 specification scenarios (TC-301 through TC-310).
- Python implementation: `src/agents/coverage_planner.py`.
- 16-test automated suite passing in CI.
