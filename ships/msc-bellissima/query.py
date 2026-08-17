"""
ships/msc-bellissima/query.py

Interactive Ground Truth Navigation & Spatial Query CLI for MSC Bellissima.
Full spatial twin interface for staterooms, routing, neighbors, and landmarks.

Examples:
    python query.py 14122
    python query.py 15666
    python query.py 20215
    python query.py --route 14122 "Marketplace Buffet"
    python query.py --route 14122 "London Theatre" --accessible
    python query.py --nearest toilet 14122
    python query.py --nearest elevator 14122
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
        print(f"\n  status                  : DOES_NOT_EXIST")
        print(f"  cabin_number            : {c_num}")
        print(f"  deck                    : {fmt(p.get('deck'))}")
        print(f"  deck_name               : {fmt(p.get('deck_name'))}")
        print(f"  review_state            : DOES_NOT_EXIST")
        print(f"\n  reason: {p.get('reason')}")
        print(f"{DIVIDER}\n")
        return

    if p.get("review_state") == "UNKNOWN":
        print(f"\n  status                  : UNKNOWN / UNMAPPED")
        print(f"  cabin_number            : {c_num}")
        print(f"  review_state            : UNKNOWN")
        print(f"\n  reason: {p.get('reason')}")
        print(f"{DIVIDER}\n")
        return

    print(f"\n  cabin_number            : {p.get('cabin_number')}")
    print(f"  deck                    : {fmt(p.get('deck'))}")
    print(f"  deck_name               : {fmt(p.get('deck_name'))}")
    print(f"  category                : {fmt(p.get('category'))}")
    print(f"  hull_side               : {fmt(p.get('hull_side'))}")
    print(f"  zone                    : {fmt(p.get('zone'))}")
    print(f"  accessible              : {fmt(p.get('accessible'))}")
    print(f"  connecting_cabin        : {fmt(p.get('connecting_cabin'))}")
    print(f"  balcony                 : {fmt(p.get('balcony'))}")
    print(f"  additional_beds         : {fmt(p.get('additional_beds'))}")
    print(f"  interior_sqm            : {fmt(p.get('interior_sqm'))} m2")
    print(f"  balcony_sqm             : {fmt(p.get('balcony_sqm'))} m2")
    print(f"  view_obstruction        : {fmt(p.get('view_obstruction'))}")
    print(f"  coordinates_norm        : x={p.get('x')}, y={p.get('y')}, z={p.get('elevation_m')}m")
    print(f"  review_state            : {fmt(p.get('review_state'))}")

    # Spatial Neighbors
    print(f"\n  -- SPATIAL ADJACENCIES --------------------------------------")
    print(f"  neighbor_left (forward) : {fmt(p.get('neighbor_left'))}")
    print(f"  neighbor_right (aft)    : {fmt(p.get('neighbor_right'))}")
    print(f"  neighbor_across         : {fmt(p.get('neighbor_across'))}")
    print(f"  stateroom_above         : {fmt(p.get('cabin_above'))}")
    print(f"  stateroom_below         : {fmt(p.get('cabin_below'))}")

    # Landmarks & Navigation
    lift = p.get("nearest_elevator", {})
    print(f"\n  -- NAVIGATION & SAFETY --------------------------------------")
    print(f"  nearest_elevator        : {lift.get('name')} ({lift.get('walking_distance_m')}m)")
    print(f"  nearest_muster_station  : {fmt(p.get('nearest_muster_station'))}")
    print(f"  corridor_snap_node      : {fmt(p.get('corridor_snap_node'))}")

    # Evidence
    print(f"\n  -- EVIDENCE PROVENANCE --------------------------------------")
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

    print(f"\n  Total Walking Distance  : {res.get('total_distance_m')} meters")
    print(f"  Estimated Walking Time  : {res.get('estimated_walking_time_sec')} seconds (~{res.get('estimated_walking_time_min')} min)")
    print(f"  Direction Turns         : {res.get('turn_count')} decision points")
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

    print(f"  Nearest Destination     : {res.get('nearest_destination').replace('TOILET_', 'Restroom ').replace('VENUE_', '')}")
    print(f"  Walking Distance        : {res.get('distance_m')} meters")
    print(f"  Estimated Walking Time  : {res.get('estimated_time_sec')} seconds")
    print(f"{DIVIDER}\n")


def print_around(location: str, radius_m: float = 30.0):
    res = engine.find_around(location, radius_m)
    print(f"\n{DIVIDER}")
    print(f"  SPATIAL SURROUNDINGS: {location} (Within {radius_m}m Radius)")
    print(DIVIDER)
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
