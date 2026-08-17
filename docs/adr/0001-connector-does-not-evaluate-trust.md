# ADR-0001: Connector Does Not Evaluate Trust

**Date**: 2026-08-17  
**Status**: `ACCEPTED`  
**Deciders**: Timonelo Architecture Group

---

## Context

The Truth Engine Connector Bridge (`src/connectors/truth_engine_bridge.py`) is the only
bridge between the Knowledge Factory and the Truth Engine. In its first implementation,
the connector contained a `TRUST_LEVEL_MAP` that mapped `source_type` values
(e.g. `OFFICIAL_SHIPYARD`) to credibility labels (e.g. `OFFICIAL`).

It also synthesized an `authority` string when no publisher was declared in the candidate.

Both behaviours constitute **trust evaluation** — an opinion about the credibility of a source
based on its classification.

---

## Decision

The connector performs **only deterministic, mechanical transformations**.  
It does not assign, derive, or infer any trust, credibility, or authority field.

Trust evaluation is exclusively the responsibility of the **Truth Engine**.

---

## Rationale

If the connector assigns trust, two problems arise:

1. **Boundary collapse**: The connector becomes a partial Truth Engine, making the
   responsibility boundary unmaintainable. Future changes to trust policy require
   modifying the connector instead of the Truth Engine.

2. **Fabricated facts**: Synthesizing `"Authority for msc-bellissima"` when no publisher
   is declared introduces a hallucinated string into the artifact record. This violates
   the zero-hallucination guarantee of the Knowledge Factory.

The alternative — keeping `TRUST_LEVEL_MAP` in the connector — was explicitly rejected.

---

## Consequences

**Positive**:
- Clean separation: adding trust logic requires only Truth Engine changes.
- No fabricated authority strings in registered artifacts.
- Connector remains trivially testable: all outputs are fully deterministic.

**Negative**:
- The Truth Engine must now receive and interpret `source_type` to derive trust,
  rather than receiving a pre-computed label.

**Neutral**:
- `artifact.schema.json` no longer requires `trust_level` in `provenance`.

---

## Compliance

Enforced by CI tests in `tests/test_truth_engine_bridge.py`:

- `test_connector_does_not_produce_trust_level`
- `test_connector_does_not_produce_authority_level`
- `test_connector_does_not_synthesize_authority_string`

Any contribution that reintroduces a trust field in the connector output will fail CI.
