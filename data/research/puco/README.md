# PUCO Government Aggregation crosswalk (pulled 2026-10-15)

Public MapServer: https://maps.puco.ohio.gov/arcgis/rest/services/misc/Government_Aggregation/MapServer/0

The service has no licenseInfo, accessInformation, or copyrightText. Polygon geometry is not stored in git. The app fetches it at runtime, and `python run_refresh.py --puco` fetches a new snapshot, into the gitignored cache `data/cache/puco/`. Each fetch writes a new file. Older snapshots stay. The map credits `Source: PUCO Government Aggregation map`.

A PUCO certificate or map listing means the government was certified as an aggregator, or belongs to a certified council. It is not proof of an active program, a current supplier, or a rate.

## Files in this folder

- `crosswalk_app_to_puco.csv` — one row per dataset zone, with matched PUCO electric polygons and flags
- `puco_map_not_in_app.csv` — 744 PUCO features that matched no app row (449 electric, 295 gas)
- `fields_summary.csv` — MapServer field list. No supplier, rate, term, or program-status fields

These tables are the 2026-10-15 flag source. A later pull should be saved as a new file. Do not overwrite these rows.

## Flag counts

- `app_zone_not_on_PUCO_electric_map`: 98, of which 13 are app-status active
- `PUCO_electric_listing_vs_app_status`: 28
- `map_NOPEC_member_vs_app_admin`: 12
- `ambiguous_multi_county_name`: 4
- `app_NOPEC_vs_map_not_NOPEC`: 1

The investigation queue shows these as flags. Zone records are not changed. The 744 unmatched listings are labeled possible prospects to research.

Matching is by normalized name, filtered by township or county type and the app county. Compound app names use the first part only. Same-name places can collide. Review flagged rows by hand.
