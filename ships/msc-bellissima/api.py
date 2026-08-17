"""
ships/msc-bellissima/api.py

FastAPI Web Service for MSC Bellissima Complete Digital Twin.
Endpoints:
- GET /ship
- GET /deck/{deck_num}
- GET /cabin/{cabin_number}
- GET /venue/{venue_name}
- GET /nearest/{target_type}?from_loc=14122
- GET /route?from_loc=14122&to_loc=Marketplace Buffet&accessible=true
- GET /distance?from_loc=14122&to_loc=Marketplace Buffet
- GET /around?location=14122&radius=30
- GET /semantic/{subject}
"""

from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import os
import sys

# Ensure local module access
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import BellissimaSpatialEngine

app = FastAPI(
    title="MSC Bellissima Spatial Digital Twin API",
    description="Multi-deck indoor navigation, spatial graph analysis, and stateroom ground truth engine.",
    version="1.0.0"
)

engine = BellissimaSpatialEngine()


@app.get("/ship")
def get_ship_profile():
    """Returns canonical vessel dimensions, registry, and build specifications."""
    return engine.ship_data


@app.get("/deck/{deck_num}")
def get_deck_details(deck_num: int):
    """Returns deck metadata, elevations, cabin ranges, and hosted venues."""
    for d in engine.decks_data:
        if d.get("deck_number") == deck_num:
            return d
    raise HTTPException(status_code=404, detail=f"Deck {deck_num} not found or omitted.")


@app.get("/cabin/{cabin_number}")
def get_cabin_details(cabin_number: str):
    """Returns stateroom ground truth profile, dimensions, and spatial neighbors."""
    return engine.get_cabin_profile(cabin_number)


@app.get("/venue/{venue_name}")
def get_venue_details(venue_name: str):
    """Returns public venue details, deck location, category, and entry coordinates."""
    v_node = engine.resolve_location_node(venue_name)
    if not v_node:
        raise HTTPException(status_code=404, detail=f"Venue '{venue_name}' not found.")

    clean_name = v_node.replace("VENUE_", "")
    for v in list(engine.restaurants_data) + list(engine.bars_data) + list(engine.pools_data) + list(engine.shops_data):
        if v.get("name") == clean_name:
            return v
    return {"name": clean_name, "node": v_node}


@app.get("/nearest/{target_type}")
def get_nearest_landmark(target_type: str, from_loc: str = Query(..., alias="from")):
    """Finds the nearest toilet, elevator, buffet, bar, or muster station."""
    res = engine.find_nearest(from_loc, target_type)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


@app.get("/route")
def get_route(
    from_loc: str = Query(..., alias="from"),
    to_loc: str = Query(..., alias="to"),
    accessible: bool = False
):
    """Computes turn-by-turn routing with walking distance, time, and step-free constraints."""
    res = engine.compute_route(from_loc, to_loc, accessible_only=accessible)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


@app.get("/distance")
def get_distance(
    from_loc: str = Query(..., alias="from"),
    to_loc: str = Query(..., alias="to")
):
    """Returns shortest walking distance in meters between any two ship locations."""
    route = engine.compute_route(from_loc, to_loc)
    if "error" in route:
        raise HTTPException(status_code=400, detail=route["error"])
    return {
        "from": from_loc,
        "to": to_loc,
        "distance_meters": route.get("total_distance_m"),
        "estimated_walking_time_sec": route.get("estimated_walking_time_sec"),
    }


@app.get("/around")
def get_around(location: str, radius: float = 30.0):
    """Finds all surrounding cabins, venues, toilets, and lifts within a walking radius in meters."""
    res = engine.find_around(location, radius_m=radius)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


@app.get("/semantic/{subject}")
def get_semantic_relations(subject: str):
    """Resolves knowledge graph edges: NEXT_TO, CONNECTED_TO, ABOVE, BELOW, NEAREST, INSIDE, PART_OF."""
    return engine.query_semantic_relations(subject)
