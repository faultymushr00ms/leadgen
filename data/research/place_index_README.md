# Ohio place index (FORGE/Prospect) — built 2026-10-15 ET

Files: `place_index.csv`, `place_zone_crosswalk.csv`, `mogadore_verification.md`. Scripts: `scripts/build_place_index.py`, `scripts/build_crosswalk.py`. Raw downloads are in `census/`.

## Sources (all downloaded 2026-10-15)
- US Census 2024 Gazetteer, Ohio places (`2024_gaz_place_39.txt`): every city (LSAD 25), village (47) and CDP (57), with GEOID and interior point.
- 2020 Census PL 94-171 redistricting geoheader (`ohgeo2020.pl`, summary level 750 = block): block population by county × county subdivision × place. Used for county split shares and containing townships (2020 boundaries, % of 2020 population).
- TIGER/Line 2024 county subdivisions and places: used for the adjacent-township test (a shared boundary longer than about 30 m) when a place is its own county subdivision, meaning it withdrew from its township (paper township) or is coextensive with one. It's also used to place GNIS points.
- Census 2020 ZCTA5–place relationship file: ZCTAs with the share of the place's land area. **A ZIP/ZCTA is not proof of jurisdiction.** ZCTAs approximate USPS ZIPs.
- USGS GNIS DomesticNames OH (file dated 2026-09-29), feature class "Populated Place": the unincorporated communities. Points inside a city or village are dropped as neighborhoods. Points with the same name as the CDP that contains them are dropped too. What remains can include hamlets, subdivisions and trailer parks.
- HIFLD Electric Retail Service Territories (ORNL/DOE ArcGIS FeatureServer, queried for the Ohio bbox): utility area-overlap shares. The data is coarse, and a small municipal system may not appear. Treat it as an indication, not a PUCO-certified boundary.
- AMP member list (amppartners.org/members, fetched 2026-10-15). A "yes" means a muni electric system exists. Some members (Columbus, Toledo, Cleveland, Hamilton) serve only part of their city. Non-AMP munis also exist, so "no" ≠ no muni.

## Columns
`type` is city, village, CDP, or unincorporated. `counties` gives % of 2020 population. `townships_containing` lists townships that contain the place's 2020 blocks. `townships_adjacent_if_withdrawn` covers places that are their own county subdivision. Adjacent cities/other municipalities are NOT listed: e.g., Clinton borders the city of New Franklin, which is the former Franklin Twp. `electric_utility_hifld` gives % of area.

## Counts
252 cities, 673 villages, 340 CDPs, and 4,375 GNIS unincorporated points (5,640 rows).

## Limits
- No Ohio Secretary of State/county auditor annexation updates were applied after the 2020 blocks and 2024 TIGER.
- Township containment comes from 2020 Census.
- Utility assignments are not PUCO-verified.
- GNIS points carry no population.
