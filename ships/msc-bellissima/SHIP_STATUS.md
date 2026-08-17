# Ship Status: MSC Bellissima — Complete Spatial Digital Twin

**Vessel**: MSC Bellissima (IMO 9760524 / 9766205)  
**Class**: Meraviglia Class  
**Shipyard**: Chantiers de l'Atlantique, Saint-Nazaire (Yard K34 / B34)  
**Canonical Topology Source**: `MSC-BEL-ART-001` (Official MSC Bellissima Deck Plan, Stand 11.2025)  
**Status**: Production-Ready Multi-Deck Spatial Digital Twin  
**Last Audit**: 2026-08-17  

---

## 1. Metrics Overview

| Dimension | Count / Status | Ground Truth Source |
|---|---|---|
| **Total Decks** | 19 decks (Decks 1-19, 14 passenger decks) | `MSC-BEL-ART-001` + Chantiers GA |
| **Cabins Discovered & Modeled** | **2,217 staterooms** (exact topology match) | `MSC-BEL-ART-001` (Pages 3–5) |
| **Public & Service Venues** | **61 venues** across 8 activity decks | `MSC-BEL-ART-001` + `MSC-BEL-ART-002` |
| **Routing Graph Nodes** | **2,384 nodes** | `routing.graphml` |
| **Routing Graph Edges** | **2,409 edges** | `routing.graphml` |
| **Spatial Distance Matrix** | Serialized Parquet dataset | `distance_matrix.parquet` |
| **Evidence Artifacts Consumed** | 5 primary & registry artifacts | Official Deckplan + IMO GISIS + Chantiers |
| **Review State** | Verified / Partial Ground Truth | No synthetic data; unsupported fields = `UNKNOWN` |

---

## 2. Canonical Deck Topology (2,217 Staterooms)

| Deck | MSC Deck Name | Staterooms | Zone Type | Key Hosted Venues |
|---:|---|---:|---|---|
| **4** | Lirica | 0 | Crew & Tender | Crew Mess, Tender Boarding Station |
| **5** | Opera | 114 | Promenade / Reception | Infinity Reception, Infinity Atrium, Medical Centre, Shore Excursions |
| **6** | Musica | 0 | Promenade / Public Atrium | Galleria Bellissima (80m LED Dome), London Theatre Lower, Il Ciliegio Restaurant |
| **7** | Fantasia | 0 | Promenade / Specialty Dining | Carousel Lounge, Casino Imperiale, Butcher's Cut, Kaito Teppanyaki |
| **8** | Meraviglia | 236 | Residential Lower | Exterior Promenade Deck & Lifeboat Stations |
| **9** | Seaside | 282 | Residential Lower | Residential Staterooms |
| **10** | Seaside Evo | 316 | Residential Lower | Residential Staterooms |
| **11** | Bellissima | 334 | Residential Lower | Residential Staterooms |
| **12** | Grandiosa | 312 | Residential Upper | Residential Staterooms |
| **13** | Magnifica | 308 | Residential Upper | Residential Staterooms |
| **14** | World Class | 243 | Residential Upper | Residential Staterooms (including Cabin 14122) |
| **15** | Preziosa | 32 | Lido / Yacht Club | Marketplace Buffet, Grand Canyon Solarium, Atmosphere Pool, Top Sail Lounge |
| **16** | Seaview | 22 | Lido / Yacht Club | Marketplace Buffet Aft Terrace, MSC Gym, MSC Aurea Spa, YC Restaurant |
| **17** | UNKNOWN | 0 | Omitted by Tradition | Excluded in standard Italian maritime numbering |
| **18** | Divina | 18 | Lido / Yacht Club | Horizon Amphitheatre & Sunset Bar, DOREMI Kids Clubs, Arizona Aquapark |
| **19** | Splendida | 0 | Lido / Yacht Club | Top Deck Solarium & The One Pool, The One Grill & Bar |
| **Total**| | **2,217** | | |

---

## 3. Consumed Evidence Artifacts

1. **`MSC-BEL-ART-001`** (Primary Canonical Deck Plan)
   - **Publisher**: MSC Cruises
   - **Document Stand**: 11.2025
   - **SHA-256**: `085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0`
   - **Scope**: 2,217 staterooms, categories, `H` accessibility markers, connecting door glyphs, 61 venues.

2. **`MSC-BEL-ART-002` / `MSC-BEL-ART-003`** (Official Web Specifications & Category Catalog)
   - **Publisher**: MSC Cruises Deutschland
   - **Scope**: Category size ranges, venue opening hours, dining classifications.

3. **`MSC-BEL-ART-005`** (Chantiers de l'Atlantique Product Sheet)
   - **Publisher**: Chantiers de l'Atlantique
   - **Scope**: Vessel length (315.83m), beam (43.0m), gross tonnage (171,598 GT), propulsion specs.

4. **`MSC-BEL-ART-008`** (IMO GISIS Registry)
   - **Publisher**: International Maritime Organization
   - **Scope**: IMO 9760524 / 9766205, Flag State Malta, call sign, dimensions.

---

## 4. Query Ground Truth Verification

- **Cabin 14122**:
  - `Deck`: 14 (World Class)
  - `Category`: `IR2` (Deluxe Interior / Innenkabine)
  - `Accessible`: `true` (Marked with `H` in canonical deck plan)
  - `Connecting Door`: `false`
  - `Balcony`: `false`
  - `Additional Beds`: `UNKNOWN` (Pending individual berth glyph extraction)
  - `Locator`: PDF Bounding Box `[82.856, 500.604, 90.651, 506.021]` on Page 5
- **Cabin 15666**: `NOT_LISTED_IN_CANONICAL_DECKPLAN` (Deck 15 contains only 32 staterooms)
- **Cabin 20215**: `NOT_LISTED_IN_CANONICAL_DECKPLAN` (Deck 20 does not exist; vessel maximum is Deck 19)
