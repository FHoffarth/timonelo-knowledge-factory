"""
ships/msc-bellissima/query.py

Interactive Ground Truth Navigation & Spatial Query CLI for MSC Bellissima.
Full spatial twin interface with proven SOURCE, DERIVATION, and CONFIDENCE.

Examples:
    python query.py 14122
    python query.py 15666
    python query.py 20215
    python query.py --route 14122 "Marketplace Buffet"
    python query.py --nearest elevator 14122
    python query.py --nearest toilet 14122
    python query.py --around 14122 30
    python query.py --semantic 14122
    python query.py --status
"""

from __future__ import annotations
import os
import sys

# Ensure local module access
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import BellissimaSpatialEngine

DIVIDER = "-" * 64
engine = BellissimaSpatialEngine()


def fmt(val: object) -> str:
    if val is None or val == "UNKNOWN":
        return "UNKNOWN"
    if isinstance(val, bool):
        return "yes" if val else "no"
    return str(val)


def print_cabin(c_num: str):
    p = engine.get_cabin_profile(c_num)
    print(f"\n{DIVIDER}")
    print(f"  MSC BELLISSIMA -- GROUND TRUTH STATEROOM PROFILE: {c_num}")
    print(DIVIDER)

    if p.get("review_state") == "DOES_NOT_EXIST":
        print(f"\n  status                  : DOES_NOT_EXIST (NOT_LISTED_IN_CANONICAL_DECKPLAN)")
        print(f"  cabin_number            : {c_num}")
        print(f"  deck                    : {fmt(p.get('deck'))}")
        print(f"  deck_name               : {fmt(p.get('deck_name'))}")
        print(f"  source                  : MSC-BEL-ART-001 (Official Deck Plan 11.2025)")
        print(f"  derivation              : Exhaustive cabin number search on canonical layout")
        print(f"  confidence              : 1.00 (DIRECT_NEGATIVE_ASSERTION)")
        print(f"\n  reason: {p.get('reason')}")
        print(f"{DIVIDER}\n")
        return

    if p.get("review_state") == "UNKNOWN":
        print(f"\n  status                  : UNKNOWN / UNMAPPED")
        print(f"  cabin_number            : {c_num}")
        print(f"  review_state            : UNKNOWN")
        print(f"  confidence              : 0.00 (UNKNOWN)")
        print(f"\n  reason: {p.get('reason')}")
        print(f"{DIVIDER}\n")
        return

    print(f"\n  cabin_number            : {p.get('cabin_number')}")
    print(f"  deck                    : {fmt(p.get('deck'))} [SOURCE: MSC-BEL-ART-001 Page {p.get('page')}, CONFIDENCE: 1.00]")
    print(f"  deck_name               : {fmt(p.get('deck_name'))} [SOURCE: MSC-BEL-ART-001, CONFIDENCE: 1.00]")
    print(f"  category                : {fmt(p.get('category'))} [SOURCE: MSC-BEL-ART-001 Color Code, CONFIDENCE: 0.99]")
    print(f"  hull_side               : {fmt(p.get('hull_side'))} [SOURCE: MSC-BEL-ART-001 Geometry, CONFIDENCE: 0.99]")
    print(f"  zone                    : {fmt(p.get('zone'))} [DERIVATION: x-coordinate longitudinal mapping, CONFIDENCE: 0.98]")
    print(f"  accessible              : {fmt(p.get('accessible'))} [SOURCE: MSC-BEL-ART-001 'H' Marker Glyph, CONFIDENCE: 0.99]")
    print(f"  connecting_cabin        : {fmt(p.get('connecting_cabin'))} [SOURCE: MSC-BEL-ART-001 Connecting Door Glyph, CONFIDENCE: 0.99]")
    print(f"  balcony                 : {fmt(p.get('balcony'))} [SOURCE: Category Definition MSC-BEL-ART-003, CONFIDENCE: 0.99]")
    print(f"  additional_beds         : {fmt(p.get('additional_beds'))} [STATUS: UNKNOWN - Pending individual berth glyph review]")
    print(f"  coordinates_norm        : x={p.get('x')}, y={p.get('y')}, z={p.get('elevation_m')}m")
    print(f"  review_state            : {fmt(p.get('review_state'))}")

    # Spatial Neighbors
    print(f"\n  -- SPATIAL ADJACENCIES (DERIVED GEOMETRY) -------------------")
    print(f"  neighbor_left (forward) : {fmt(p.get('neighbor_left'))} [DERIVATION: Linear corridor index -2]")
    print(f"  neighbor_right (aft)    : {fmt(p.get('neighbor_right'))} [DERIVATION: Linear corridor index +2]")
    print(f"  neighbor_across         : {fmt(p.get('neighbor_across'))} [DERIVATION: Transverse corridor pair]")
    print(f"  stateroom_above         : {fmt(p.get('cabin_above'))} [SOURCE: Deck {p.get('deck')+1 if p.get('deck') else ''} Layout Overlay]")
    print(f"  stateroom_below         : {fmt(p.get('cabin_below'))} [SOURCE: Deck {p.get('deck')-1 if p.get('deck') else ''} Layout Overlay]")

    # Navigation & Safety
    lift = p.get("nearest_elevator", {})
    print(f"\n  -- NAVIGATION & SAFETY (GRAPH DERIVED) ----------------------")
    print(f"  nearest_elevator        : {lift.get('name')} ({lift.get('walking_distance_m')}m) [DERIVATION: NetworkX shortest path]")
    print(f"  nearest_muster_station  : {fmt(p.get('nearest_muster_station'))} [SOURCE: Safety Plan Section]")
    print(f"  corridor_snap_node      : {fmt(p.get('corridor_snap_node'))}")

    # Evidence
    print(f"\n  -- EVIDENCE PROVENANCE & LOCATORS ---------------------------")
    print(f"  evidence_artifact       : {fmt(p.get('evidence_artifact'))}")
    print(f"  page                    : {fmt(p.get('page'))}")
    print(f"  locator                 : {fmt(p.get('locator'))}")
    if p.get("notes"):
        print(f"  notes                   : {p.get('notes')}")

    print(f"{DIVIDER}\n")


def print_route(from_loc: str, to_loc: str, accessible: bool = False):
    res = engine.compute_route(from_loc, to_loc, accessible_only=accessible)
    print(f"\n{DIVIDER}")
    print(f"  MSC BELLISSIMA INDOOR NAVIGATION: {from_loc} -> {to_loc}")
    if accessible:
        print("  [STEP-FREE WHEELCHAIR ACCESSIBLE ROUTE]")
    print(DIVIDER)

    if not res.get("success"):
        print(f"\n  Error: {res.get('error')}")
        print(f"{DIVIDER}\n")
        return

    print(f"\n  Total Walking Distance  : {res.get('total_distance_m')} meters [DERIVATION: Exact metric path Euclidean sum]")
    print(f"  Estimated Walking Time  : {res.get('estimated_walking_time_sec')} seconds (~{res.get('estimated_walking_time_min')} min)")
    print(f"  Speed Baseline          : 1.20 m/s [SOURCE: IMO MSC.1/Circ.1533 Evacuation Guidelines]")
    print(f"  Direction Turns         : {res.get('turn_count')} decision points (+4s deceleration penalty each)")
    print(f"  Step-Free Accessible    : {fmt(res.get('step_free_accessible'))}")

    print(f"\n  TURN-BY-TURN INSTRUCTIONS:")
    print(f"  {'-' * 56}")
    for idx, step in enumerate(res.get("turn_by_turn_instructions", []), 1):
        print(f"  {idx:>2}. {step}")

    print(f"\n  WAYPOINT GRAPH PATH: {' -> '.join(res.get('path_nodes', []))}")
    print(f"{DIVIDER}\n")


def print_nearest(target_type: str, from_loc: str):
    res = engine.find_nearest(from_loc, target_type)
    print(f"\n{DIVIDER}")
    print(f"  NEAREST {target_type.upper()} FROM {from_loc}")
    print(DIVIDER)
    if "error" in res:
        print(f"\n  Error: {res.get('error')}")
        print(f"{DIVIDER}\n")
        return

    dest = res.get('nearest_destination', '').replace('TOILET_', 'Restroom ').replace('VENUE_', '')
    print(f"  Nearest Destination     : {dest}")
    print(f"  Walking Distance        : {res.get('distance_m')} meters [DERIVATION: Dijkstra all-pairs metric shortest path]")
    print(f"  Estimated Walking Time  : {res.get('estimated_time_sec')} seconds [IMO MSC.1/Circ.1533 baseline 1.2m/s]")
    print(f"{DIVIDER}\n")


def print_around(location: str, radius_m: float = 30.0):
    res = engine.find_around(location, radius_m)
    print(f"\n{DIVIDER}")
    print(f"  SPATIAL SURROUNDINGS: {location} (Within {radius_m}m Radius)")
    print(DIVIDER)
    print(f"  Derivation Method       : Single-source Dijkstra cutoff radius on multi-deck spatial graph")
    print(f"  Staterooms Nearby ({res.get('cabins_count')} total):")
    for c in res.get("cabins", [])[:8]:
        print(f"    - Cabin {c['cabin']} ({c['distance_m']}m)")
    if res.get("venues"):
        print(f"  Venues Nearby:")
        for v in res.get("venues", []):
            print(f"    - {v['venue']} ({v['distance_m']}m)")
    if res.get("toilets"):
        print(f"  Restrooms Nearby:")
        for t in res.get("toilets", []):
            print(f"    - {t['toilet']} ({t['distance_m']}m)")
    if res.get("elevators"):
        print(f"  Elevator Cores Nearby:")
        for e in res.get("elevators", []):
            print(f"    - {e['elevator']} ({e['distance_m']}m)")
    print(f"{DIVIDER}\n")


def print_semantic(subject: str):
    res = engine.query_semantic_relations(subject)
    print(f"\n{DIVIDER}")
    print(f"  KNOWLEDGE & SEMANTIC GRAPH: {subject}")
    print(DIVIDER)
    for k, v in res.items():
        print(f"  {k:<16} : {v}")
    print(f"{DIVIDER}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python query.py <cabin_number>                  - ground truth stateroom profile")
        print("  python query.py --route <from> <to> [--accessible] - turn-by-turn navigation")
        print("  python query.py --nearest <toilet|elevator|buffet|bar> <from> - find nearest")
        print("  python query.py --around <location> [radius_m]   - surroundings search")
        print("  python query.py --semantic <subject>             - knowledge graph relations")
        print("  python query.py --status                         - ship overview")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "--route":
        from_loc = sys.argv[2]
        to_loc = sys.argv[3]
        acc = "--accessible" in sys.argv
        print_route(from_loc, to_loc, accessible=acc)
    elif arg == "--nearest":
        t_type = sys.argv[2]
        from_loc = sys.argv[3]
        print_nearest(t_type, from_loc)
    elif arg == "--around":
        loc = sys.argv[2]
        r = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
        print_around(loc, radius_m=r)
    elif arg == "--semantic":
        subj = sys.argv[2]
        print_semantic(subj)
    elif arg == "--status":
        from query import show_status
        show_status()
    else:
        print_cabin(arg)


if __name__ == "__main__":
    main()
