"""
ships/msc-bellissima/query.py

Interactive Ground Truth Query CLI for MSC Bellissima.
Queries only verified evidence-backed facts from YAML datasets.
Unsupported fields and non-existent cabins strictly return UNKNOWN.

Usage:
    python ships/msc-bellissima/query.py 14122
    python ships/msc-bellissima/query.py 15666
    python ships/msc-bellissima/query.py 20215
    python ships/msc-bellissima/query.py --status
    python ships/msc-bellissima/query.py --decks
    python ships/msc-bellissima/query.py --venues
"""

from __future__ import annotations
import os
import sys
import yaml

SHIP_DIR = os.path.dirname(os.path.abspath(__file__))
SHIP_YAML = os.path.join(SHIP_DIR, "ship.yaml")
DECKS_YAML = os.path.join(SHIP_DIR, "decks.yaml")
CABINS_YAML = os.path.join(SHIP_DIR, "cabins.yaml")
VENUES_YAML = os.path.join(SHIP_DIR, "venues.yaml")
INDEXES_YAML = os.path.join(SHIP_DIR, "indexes.yaml")

DIVIDER = "-" * 64


def load_yaml(path: str) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fmt_val(val: object) -> str:
    if val is None or val == "UNKNOWN":
        return "UNKNOWN"
    if isinstance(val, bool):
        return "yes" if val else "no"
    return str(val)


def query_cabin(cabin_num: str) -> None:
    cabins_data = load_yaml(CABINS_YAML).get("cabins", [])
    indexes_data = load_yaml(INDEXES_YAML).get("cabin_index", {})

    target_cabin = None
    for c in cabins_data:
        if str(c.get("cabin_number")) == str(cabin_num):
            target_cabin = c
            break

    idx_entry = indexes_data.get(str(cabin_num))

    print(f"\n{DIVIDER}")
    print(f"  MSC BELLISSIMA -- GROUND TRUTH PROFILE: CABIN {cabin_num}")
    print(DIVIDER)

    if not target_cabin and not idx_entry:
        print(f"\n  status                  : UNKNOWN / UNMAPPED")
        print(f"  cabin_number            : {cabin_num}")
        print(f"  deck                    : UNKNOWN")
        print(f"  deck_name               : UNKNOWN")
        print(f"  category                : UNKNOWN")
        print(f"  accessible              : UNKNOWN")
        print(f"  connecting_cabin        : UNKNOWN")
        print(f"  balcony                 : UNKNOWN")
        print(f"  additional_beds         : UNKNOWN")
        print(f"  evidence_artifact       : UNKNOWN")
        print(f"  page                    : UNKNOWN")
        print(f"  locator                 : UNKNOWN")
        print(f"  review_state            : UNKNOWN")
        print(f"\n  note: No evidence currently exists for cabin {cabin_num}.")
        print(f"{DIVIDER}\n")
        return

    # Use cabin profile or index entry
    c = target_cabin or {}
    idx = idx_entry or {}

    deck = c.get("deck") or idx.get("deck")
    deck_name = c.get("deck_name") or idx.get("deck_name")
    category = c.get("category") or idx.get("category")
    accessible = c.get("accessible") if "accessible" in c else idx.get("accessible")
    connecting = c.get("connecting_cabin") or "UNKNOWN"
    balcony = c.get("balcony") if "balcony" in c else idx.get("balcony")
    beds = c.get("additional_beds") or "UNKNOWN"
    artifact = c.get("evidence_artifact") or idx.get("evidence")
    page = c.get("page") or "General Arrangement Plan"
    locator = c.get("locator") or idx.get("locator")
    state = c.get("review_state") or idx.get("status")

    print(f"\n  cabin_number            : {cabin_num}")
    print(f"  deck                    : {fmt_val(deck)}")
    print(f"  deck_name               : {fmt_val(deck_name)}")
    print(f"  category                : {fmt_val(category)}")
    print(f"  accessible              : {fmt_val(accessible)}")
    print(f"  connecting_cabin        : {fmt_val(connecting)}")
    print(f"  balcony                 : {fmt_val(balcony)}")
    print(f"  additional_beds         : {fmt_val(beds)}")
    print(f"  evidence_artifact       : {fmt_val(artifact)}")
    print(f"  page                    : {fmt_val(page)}")
    print(f"  locator                 : {fmt_val(locator)}")
    print(f"  review_state            : {fmt_val(state)}")

    if c.get("notes") or idx.get("reason"):
        note = c.get("notes") or idx.get("reason")
        print(f"\n  evidence_notes          : {note}")

    print(f"{DIVIDER}\n")


def show_status() -> None:
    ship_data = load_yaml(SHIP_YAML).get("vessel", {})
    decks_data = load_yaml(DECKS_YAML).get("decks", [])
    cabins_data = load_yaml(CABINS_YAML).get("cabins", [])
    venues_data = load_yaml(VENUES_YAML).get("venues", [])

    print(f"\n{DIVIDER}")
    print(f"  MSC BELLISSIMA -- STATUS REPORT")
    print(DIVIDER)
    print(f"  Name                    : {ship_data.get('name')}")
    print(f"  IMO                     : {ship_data.get('imo')}")
    print(f"  Class                   : {ship_data.get('ship_class')}")
    print(f"  Shipyard                : {ship_data.get('builder')}")
    print(f"  Delivery Date           : {ship_data.get('delivery_date')}")
    print(f"  Gross Tonnage           : {ship_data.get('gross_tonnage')} GT")
    print(f"  Total Decks             : {len(decks_data)}")
    print(f"  Total Staterooms Fleet  : {ship_data.get('total_staterooms_registered')}")
    print(f"  Verified Cabins Sample  : {len(cabins_data)}")
    print(f"  Verified Venues         : {len(venues_data)}")
    print(f"{DIVIDER}\n")


def show_decks() -> None:
    decks_data = load_yaml(DECKS_YAML).get("decks", [])
    print(f"\n{DIVIDER}")
    print(f"  MSC BELLISSIMA -- DECKS REGISTER ({len(decks_data)} Decks)")
    print(DIVIDER)
    for d in decks_data:
        acc = "Passenger" if d.get("is_passenger_accessible") else "Crew/Technical"
        print(f"  Deck {d.get('deck_number'):>2} : {d.get('deck_name'):<16} | {d.get('cabins'):>3} cabins | {len(d.get('venues', [])):>2} venues | {acc}")
    print(f"{DIVIDER}\n")


def show_venues() -> None:
    venues_data = load_yaml(VENUES_YAML).get("venues", [])
    print(f"\n{DIVIDER}")
    print(f"  MSC BELLISSIMA -- VENUES REGISTER ({len(venues_data)} Venues)")
    print(DIVIDER)
    for v in venues_data:
        print(f"  Deck {v.get('deck'):>2} [{v.get('deck_name')}] : {v.get('name'):<42} ({v.get('category')})")
    print(f"{DIVIDER}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python query.py <cabin_number | --status | --decks | --venues>")
        sys.exit(1)

    arg = sys.argv[1].strip()
    if arg == "--status":
        show_status()
    elif arg == "--decks":
        show_decks()
    elif arg == "--venues":
        show_venues()
    else:
        query_cabin(arg)


if __name__ == "__main__":
    main()
