# FORGE Daily Audit — 2026-10-23

**456 findings** | HIGH: 15  MEDIUM: 296  LOW: 145
Zones checked: 327 | Elapsed: 0.01s

## 🆕 New since 2026-10-22 (456)

- `HIGH` **Stark County (Unincorporated / Remaining)** (Akron / Canton) — `EXPIRED_ACTIVE`: termEnd=2026-08-31 passed 53d ago but status='pain_coming' — should be rollover
- `HIGH` **Golf Manor** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Wayne Township (Warren Co)** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Batavia Township** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Pierce Township / Amelia** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Williamsburg** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Seven Mile** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2025-09-30 expired 388d ago — any new contract?
- `HIGH` **Seven Mile** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Oxford Township (Butler Co)** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Madison Township (Butler Co)** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Lemon Township** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Cheviot** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Madeira** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Lakewood** (NE Ohio / Cleveland / NOPEC) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **East Cleveland** (NE Ohio / Cleveland / NOPEC) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `LOW` **Akron** (Akron / Canton) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.24 but sourceUrl=null
- `LOW` **Akron** (Akron / Canton) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Green** (Akron / Canton) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.24 but sourceUrl=null
- `LOW` **Green** (Akron / Canton) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Medina County** (Akron / Canton) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.5 but sourceUrl=null
- `LOW` **Kent / Portage County** (Akron / Canton) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Sharonville** (Cincinnati / SW Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.39 but sourceUrl=null
- `LOW` **Reading** (Cincinnati / SW Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.29 but sourceUrl=null
- `LOW` **Norwood** (Cincinnati / SW Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.39 but sourceUrl=null
- `LOW` **Cincinnati** (Cincinnati / SW Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.44 but sourceUrl=null
- `LOW` **Deer Park** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Hamilton Township (Warren Co)** (Cincinnati / SW Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.2 but sourceUrl=null
- `LOW` **Hamilton Township (Warren Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Liberty Township (Butler Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Tate Township** (Cincinnati / SW Ohio) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['municipal utility']
- `LOW` **Seven Mile** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Cleveland** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.236 but sourceUrl=null
- `LOW` **Parma** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Strongsville** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Euclid** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Solon** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **North Royalton** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Berea** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Columbus** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.01 but sourceUrl=null
- `LOW` **Gahanna** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **Grove City** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.97 but sourceUrl=null
- `LOW` **Ontario** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=8.66 but sourceUrl=null
- `LOW` **Dayton** (Dayton / Miami Valley) — `RATE_NO_SOURCE`: confirmed agg with currentRate=8.71 but sourceUrl=null
- `LOW` **Dayton** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Riverside** (Dayton / Miami Valley) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.333 but sourceUrl=null
- `LOW` **Riverside** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Fairborn** (Dayton / Miami Valley) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.04 but sourceUrl=null
- `LOW` **Mentor** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Willoughby** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Eastlake** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Wickliffe** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Lake County (NOPEC Group)** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Geneva** (Ashtabula County) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Conneaut** (Ashtabula County) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Jackson Township (Stark)** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Perry Township (Stark)** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Andover** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.86 but sourceUrl=null
- `LOW` **North Olmsted** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Middleburg Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Brook Park** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Broadview Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Seven Hills** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Garfield Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Maple Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Mayfield Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Highland Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Richmond Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Lyndhurst** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **South Euclid** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **University Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Cleveland Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Shaker Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Rocky River** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Bay Village** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Fairview Park** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Olmsted Falls** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Bedford Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Warrensville Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Twinsburg** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Parma Heights** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Beachwood** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Independence** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Bedford** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Pepper Pike** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Avon** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Avon Lake** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **North Ridgeville** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Amherst** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Sheffield Lake** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Sheffield Village** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Grafton** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Stow** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Tallmadge** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Barberton** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Norton** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Copley Township** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Aurora** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Streetsboro** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Ravenna** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Painesville** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Willoughby Hills** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Mentor-on-the-Lake** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Madison Township** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Bainbridge Township** (NE Ohio / Cleveland / NOPEC) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Cleveland Public Power** (Municipal Utilities) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['municipal utility']
- `LOW` **Brunswick** (Other Ohio Markets) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Medina City** (Other Ohio Markets) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.5 but sourceUrl=null
- `LOW` **Lorain (City)** (Other Ohio Markets) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.999 but sourceUrl=null
- `LOW` **Licking County / Pataskala** (Other Ohio Markets) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.01 but sourceUrl=null
- `LOW` **Grove City Area / Southwest Franklin County** (Other Ohio Markets) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.97 but sourceUrl=null
- `LOW` **Dublin** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **Hilliard** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **Worthington** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **Reynoldsburg** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **New Albany** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **Bexley** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **Grandview Heights** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=11.162 but sourceUrl=null
- `LOW` **Lancaster** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.01 but sourceUrl=null
- `LOW` **Delaware (City)** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.01 but sourceUrl=null
- `LOW` **Pickerington** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.01 but sourceUrl=null
- `LOW` **Heath / Newark** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.01 but sourceUrl=null
- `LOW` **Marysville** (Columbus / Central Ohio) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.01 but sourceUrl=null
- `LOW` **Toledo** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Toledo** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Perrysburg** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Perrysburg** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Maumee** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Maumee** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Sylvania** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Sylvania** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Oregon** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Oregon** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Lucas County Unincorporated** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Rossford** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Rossford** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Northwood** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Northwood** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Waterville** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Waterville** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Whitehouse** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Whitehouse** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Holland** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Holland** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Jerusalem Township** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Jerusalem Township** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Washington Township (Wood)** (Greater Toledo) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.75 but sourceUrl=null
- `LOW` **Washington Township (Wood)** (Greater Toledo) — `STALE_60`: lastVerified=2026-08-19 (65d ago)
- `LOW` **Austintown Township** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.59 but sourceUrl=null
- `LOW` **Howland Township** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.14 but sourceUrl=null
- `LOW` **Weathersfield Township** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.14 but sourceUrl=null
- `LOW` **Vienna Township** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.14 but sourceUrl=null
- `LOW` **Champion Township** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.14 but sourceUrl=null
- `LOW` **Bazetta Township** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.14 but sourceUrl=null
- `LOW` **Bazetta Township** (Youngstown / Warren) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['municipal utility']
- `LOW` **Springfield Township (Mahoning)** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.59 but sourceUrl=null
- `LOW` **Jackson Township (Mahoning)** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.59 but sourceUrl=null
- `LOW` **Coitsville Township** (Youngstown / Warren) — `RATE_NO_SOURCE`: confirmed agg with currentRate=10.59 but sourceUrl=null
- `LOW` **CLAUDE.md** (Documentation) — `DOC_COUNT_MISMATCH`: CLAUDE.md claims 251 zones but actual=327
- `LOW` **CLAUDE.md** (Documentation) — `DOC_COUNT_MISMATCH`: CLAUDE.md claims 18 JSON files but actual=19
- `MEDIUM` **Akron** (Akron / Canton) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Green** (Akron / Canton) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Medina County** (Akron / Canton) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Stark County (Unincorporated / Remaining)** (Akron / Canton) — `TERM_NO_PROGRAM`: has term dates but supplier=null and agg='address_dependent'
- `MEDIUM` **Stark County (Unincorporated / Remaining)** (Akron / Canton) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Stark County (Unincorporated / Remaining)** (Akron / Canton) — `COPY_RATE_MISMATCH`: hook mentions 9.999¢ but currentRate=9.77, previousRate=None
- `MEDIUM` **Kent / Portage County** (Akron / Canton) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Kent / Portage County** (Akron / Canton) — `COPY_RATE_MISMATCH`: takeaway mentions 8.999¢ but currentRate=9.999, previousRate=7.0
- `MEDIUM` **Clinton** (Akron / Canton) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Sharonville** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Reading** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Norwood** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Norwood** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 7.03¢ but currentRate=10.39, previousRate=6.67
- `MEDIUM` **Cincinnati** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **West Chester Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Mason** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Blue Ash** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Montgomery** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Anderson Township** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Anderson Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Anderson Township** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.86, previousRate=None
- `MEDIUM` **Anderson Township** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=9.86, previousRate=None
- `MEDIUM` **Fairfield** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Fairfield** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Fairfield** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.39, previousRate=None
- `MEDIUM` **Milford** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Loveland** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Loveland** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Loveland** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.07, previousRate=None
- `MEDIUM` **Springdale** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.29, previousRate=None
- `MEDIUM` **Springdale** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=9.29, previousRate=None
- `MEDIUM` **Kenwood / Symmes Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Colerain Township** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Colerain Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Colerain Township** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.36, previousRate=None
- `MEDIUM` **Colerain Township** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=9.36, previousRate=None
- `MEDIUM` **Delhi Township** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Delhi Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Delhi Township** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=9.32, previousRate=None
- `MEDIUM` **Forest Park** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Forest Park** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Silverton** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Silverton** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Clearcreek Township** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Clearcreek Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Hamilton Township (Warren Co)** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.2, previousRate=None
- `MEDIUM` **Sycamore Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Sycamore Township** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=10.21, previousRate=9.23
- `MEDIUM` **Springfield Township (Hamilton Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Springfield Township (Hamilton Co)** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=10.29, previousRate=9.45
- `MEDIUM` **Green Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Lockland** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Union Township (Clermont Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Miami Township (Clermont Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Golf Manor** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Waynesville** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Waynesville** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Waynesville** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.14, previousRate=None
- `MEDIUM` **Waynesville** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=9.14, previousRate=None
- `MEDIUM` **Franklin** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **South Lebanon** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Turtlecreek Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Wayne Township (Warren Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Springboro** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Morrow** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Batavia Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Pierce Township / Amelia** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Williamsburg** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Tate Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Goshen Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **New Richmond** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Oxford** (Cincinnati / SW Ohio) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Oxford** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Seven Mile** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=None, previousRate=6.23
- `MEDIUM` **Seven Mile** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=None, previousRate=6.23
- `MEDIUM` **Harrison** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.7¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Harrison** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: hook mentions 10.7¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Monroe** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Oxford Township (Butler Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Madison Township (Butler Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Lemon Township** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Trenton** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Cheviot** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Madeira** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Mount Healthy** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Miami Township (Hamilton Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **St. Bernard** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Morgan Township (Butler Co)** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **Cleveland** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Lakewood** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **East Cleveland** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Parma** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Strongsville** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Euclid** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Solon** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **North Royalton** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Berea** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Columbus** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Gahanna** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Gahanna** (Columbus / Central Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.927¢ but currentRate=11.162, previousRate=9.756
- `MEDIUM` **Grove City** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Ontario** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Beavercreek** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Huber Heights** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Miamisburg** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Springboro** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Xenia** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Franklin** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Springfield** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Urbana** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Centerville** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Vandalia** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Dayton** (Dayton / Miami Valley) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Dayton** (Dayton / Miami Valley) — `RATE_CHANGE_NO_PREV`: rateChange=22.7% set but previousRate=null
- `MEDIUM` **Dayton** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 10.691¢ but currentRate=8.71, previousRate=None
- `MEDIUM` **Dayton** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: hook mentions 10.69¢ but currentRate=8.71, previousRate=None
- `MEDIUM` **Riverside** (Dayton / Miami Valley) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Fairborn** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Troy** (Dayton / Miami Valley) — `STALE_RENEWAL`: rollover termEnd=2025-12-31 expired 296d ago — any new contract?
- `MEDIUM` **Troy** (Dayton / Miami Valley) — `TERM_NO_PROGRAM`: has term dates but supplier=null and agg='no_aggregation_verified'
- `MEDIUM` **Troy** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Middletown** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Kettering** (Dayton / Miami Valley) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Zanesville** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Cambridge** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Athens / Ohio University Area** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Chillicothe** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Circleville** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Logan** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Gallipolis** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Portsmouth** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Ironton** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Jackson** (Eastern Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Mentor** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Willoughby** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Eastlake** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Wickliffe** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Lake County (NOPEC Group)** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Chardon / Geauga County** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Niles** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Girard** (NE Ohio / Cleveland / NOPEC) — `STALE_RENEWAL`: rollover termEnd=2025-12-31 expired 296d ago — any new contract?
- `MEDIUM` **Girard** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Girard** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 9.38¢ but currentRate=6.88, previousRate=None
- `MEDIUM` **Boardman Township** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Canfield** (NE Ohio / Cleveland / NOPEC) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Canfield** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Salem** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Alliance** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Ashtabula** (Ashtabula County) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Geneva** (Ashtabula County) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Conneaut** (Ashtabula County) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Mansfield** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Wooster** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **New Philadelphia / Tuscarawas County** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Coshocton** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Plain Township** (NE Ohio / Cleveland / NOPEC) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Plain Township** (NE Ohio / Cleveland / NOPEC) — `TERM_NO_PROGRAM`: has term dates but supplier=null and agg='no_aggregation_verified'
- `MEDIUM` **Plain Township** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Canton** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **North Canton** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Massillon** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Perry Township (Stark)** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Andover** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-03 (142d ago)
- `MEDIUM` **North Olmsted** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Middleburg Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Brook Park** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Broadview Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Seven Hills** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Garfield Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Maple Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Mayfield Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Highland Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Richmond Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Lyndhurst** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **South Euclid** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **University Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Cleveland Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Shaker Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Rocky River** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Bay Village** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Fairview Park** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Olmsted Falls** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Bedford Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Warrensville Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Twinsburg** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Parma Heights** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Beachwood** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Independence** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Bedford** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Pepper Pike** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Avon** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Avon Lake** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **North Ridgeville** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Amherst** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Sheffield Lake** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Sheffield Village** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Grafton** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Stow** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Tallmadge** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Barberton** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Norton** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Copley Township** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Aurora** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Streetsboro** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Ravenna** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Painesville** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Willoughby Hills** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Mentor-on-the-Lake** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Madison Township** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Bainbridge Township** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Newbury Township** (NE Ohio / Cleveland / NOPEC) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Findlay** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Lima** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Fremont** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Tiffin** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Defiance** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Sandusky** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Port Clinton** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Bucyrus** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Kenton** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Bellefontaine** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Washington Court House** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Wilmington** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Ashland** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Marion** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Fostoria** (NW & Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Darke Rural Electric** (Electric Cooperatives) — `COOP_IOU_NOTES`: electric_cooperative zone but notes reference IOU names: ['AES Ohio']
- `MEDIUM` **Holmes-Wayne Electric** (Electric Cooperatives) — `COOP_IOU_NOTES`: electric_cooperative zone but notes reference IOU names: ['Ohio Edison']
- `MEDIUM` **Mid-Ohio Energy** (Electric Cooperatives) — `COOP_IOU_NOTES`: electric_cooperative zone but notes reference IOU names: ['Ohio Edison']
- `MEDIUM` **South Central Power** (Electric Cooperatives) — `COOP_IOU_NOTES`: electric_cooperative zone but notes reference IOU names: ['AEP Ohio']
- `MEDIUM` **Cleveland Public Power** (Municipal Utilities) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Columbus Division of Power** (Municipal Utilities) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Piqua** (Municipal Utilities) — `MUNI_IOU_NOTES`: municipal_utility zone but notes reference IOU names: ['AES Ohio']
- `MEDIUM` **Hamilton** (Municipal Utilities) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Brunswick** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Medina City** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Elyria** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Lorain (City)** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Struthers** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Poland Township** (Other Ohio Markets) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Poland Township** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Licking County / Pataskala** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Grove City Area / Southwest Franklin County** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Athens County (Rural AEP)** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Guernsey / Noble / Morgan Counties** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Medina County (Rural Unincorporated)** (Other Ohio Markets) — `TERM_NO_PROGRAM`: has term dates but supplier=null and agg='address_dependent'
- `MEDIUM` **Medina County (Rural Unincorporated)** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Lakeview / Indian Lake Area** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Steubenville** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Marietta** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **McConnelsville / Morgan County** (Other Ohio Markets) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Dublin** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Hilliard** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Worthington** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Reynoldsburg** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **New Albany** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Bexley** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Grandview Heights** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Westerville** (Columbus / Central Ohio) — `MUNI_IOU_NOTES`: municipal_utility zone but notes reference IOU names: ['AEP Ohio']
- `MEDIUM` **Lancaster** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Delaware (City)** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Pickerington** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Heath / Newark** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Marysville** (Columbus / Central Ohio) — `STALE_60`: lastVerified=2026-05-01 (175d ago)
- `MEDIUM` **Toledo** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Perrysburg** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Maumee** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Sylvania** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Oregon** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Lucas County Unincorporated** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Rossford** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Northwood** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Waterville** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Whitehouse** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Holland** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Jerusalem Township** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Washington Township (Wood)** (Greater Toledo) — `STALE_RENEWAL`: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- `MEDIUM` **Youngstown** (Youngstown / Warren) — `STALE_RENEWAL`: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- `MEDIUM` **Youngstown** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Trumbull County** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Mahoning County** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Warren City** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Sebring** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Austintown Township** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-01 (144d ago)
- `MEDIUM` **Howland Township** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Liberty Township (Trumbull)** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Brookfield Township (Trumbull)** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Weathersfield Township** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Vienna Township** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Champion Township** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Bazetta Township** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Campbell** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Springfield Township (Mahoning)** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Jackson Township (Mahoning)** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)
- `MEDIUM` **Coitsville Township** (Youngstown / Warren) — `STALE_60`: lastVerified=2026-06-04 (141d ago)

## NE Ohio / Cleveland / NOPEC (HIGH:2 MED:85 LOW:63)

- `HIGH` **Lakewood** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **East Cleveland** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Cleveland** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Lakewood** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **East Cleveland** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Parma** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Strongsville** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Euclid** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Solon** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **North Royalton** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Berea** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Mentor** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Willoughby** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Eastlake** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Wickliffe** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Lake County (NOPEC Group)** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Chardon / Geauga County** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Niles** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Girard** `STALE_RENEWAL`  
  rollover termEnd=2025-12-31 expired 296d ago — any new contract?
  *current:* `2025-12-31`
- `MEDIUM` **Girard** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Girard** `COPY_RATE_MISMATCH`  
  hook mentions 9.38¢ but currentRate=6.88, previousRate=None
  *current:* `9.38`
- `MEDIUM` **Boardman Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Canfield** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Canfield** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Salem** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Alliance** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Mansfield** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Wooster** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **New Philadelphia / Tuscarawas County** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Coshocton** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Plain Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Plain Township** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='no_aggregation_verified'
  *current:* `None → 2026-05-31`
- `MEDIUM` **Plain Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Canton** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **North Canton** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Massillon** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Perry Township (Stark)** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Andover** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **North Olmsted** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Middleburg Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Brook Park** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Broadview Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Seven Hills** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Garfield Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Maple Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Mayfield Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Highland Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Richmond Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Lyndhurst** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **South Euclid** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **University Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Cleveland Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Shaker Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Rocky River** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Bay Village** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Fairview Park** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Olmsted Falls** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Bedford Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Warrensville Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Twinsburg** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Parma Heights** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Beachwood** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Independence** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Bedford** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Brecksville** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Pepper Pike** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Avon** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Avon Lake** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **North Ridgeville** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Amherst** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Sheffield Lake** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Sheffield Village** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Grafton** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Stow** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Tallmadge** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Barberton** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Norton** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Copley Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Aurora** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Streetsboro** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Ravenna** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Painesville** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Willoughby Hills** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Mentor-on-the-Lake** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Madison Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Bainbridge Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Newbury Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `LOW` **Cleveland** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.236 but sourceUrl=null
  *current:* `9.236`
- `LOW` **Parma** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Strongsville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Euclid** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Solon** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **North Royalton** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Berea** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Mentor** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Willoughby** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Eastlake** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Wickliffe** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Lake County (NOPEC Group)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Jackson Township (Stark)** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Perry Township (Stark)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Andover** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.86 but sourceUrl=null
  *current:* `9.86`
- `LOW` **North Olmsted** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Middleburg Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Brook Park** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Broadview Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Seven Hills** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Garfield Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Maple Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Mayfield Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Highland Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Richmond Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Lyndhurst** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **South Euclid** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **University Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Cleveland Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Shaker Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Rocky River** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Bay Village** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Fairview Park** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Olmsted Falls** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Bedford Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Warrensville Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Twinsburg** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Parma Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Beachwood** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Independence** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Bedford** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Brecksville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Pepper Pike** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Avon** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Avon Lake** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **North Ridgeville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Amherst** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Sheffield Lake** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Sheffield Village** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Grafton** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Stow** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Tallmadge** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Barberton** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Norton** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Copley Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Aurora** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Streetsboro** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Ravenna** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Painesville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Willoughby Hills** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Mentor-on-the-Lake** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Madison Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Bainbridge Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`

## Ashtabula County (HIGH:0 MED:3 LOW:2)

- `MEDIUM` **Ashtabula** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Geneva** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Conneaut** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `LOW` **Geneva** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Conneaut** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`

## Akron / Canton (HIGH:1 MED:9 LOW:6)

- `HIGH` **Stark County (Unincorporated / Remaining)** `EXPIRED_ACTIVE`  
  termEnd=2026-08-31 passed 53d ago but status='pain_coming' — should be rollover
  *current:* `2026-08-31`
- `MEDIUM` **Akron** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Green** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Medina County** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Stark County (Unincorporated / Remaining)** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='address_dependent'
  *current:* `2025-08-01 → 2026-08-31`
- `MEDIUM` **Stark County (Unincorporated / Remaining)** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Stark County (Unincorporated / Remaining)** `COPY_RATE_MISMATCH`  
  hook mentions 9.999¢ but currentRate=9.77, previousRate=None
  *current:* `9.999`
- `MEDIUM` **Kent / Portage County** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Kent / Portage County** `COPY_RATE_MISMATCH`  
  takeaway mentions 8.999¢ but currentRate=9.999, previousRate=7.0
  *current:* `8.999`
- `MEDIUM` **Clinton** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `LOW` **Akron** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.24 but sourceUrl=null
  *current:* `9.24`
- `LOW` **Akron** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Green** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.24 but sourceUrl=null
  *current:* `9.24`
- `LOW` **Green** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Medina County** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.5 but sourceUrl=null
  *current:* `9.5`
- `LOW` **Kent / Portage County** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`

## Youngstown / Warren (HIGH:0 MED:18 LOW:10)

- `MEDIUM` **Youngstown** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Youngstown** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Trumbull County** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Mahoning County** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Warren City** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sebring** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Austintown Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Howland Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Liberty Township (Trumbull)** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Brookfield Township (Trumbull)** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Weathersfield Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Vienna Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Champion Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Bazetta Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Campbell** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Springfield Township (Mahoning)** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Jackson Township (Mahoning)** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Coitsville Township** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `LOW` **Austintown Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.59 but sourceUrl=null
  *current:* `10.59`
- `LOW` **Howland Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Weathersfield Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Vienna Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Champion Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Bazetta Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Bazetta Township** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **Springfield Township (Mahoning)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.59 but sourceUrl=null
  *current:* `10.59`
- `LOW` **Jackson Township (Mahoning)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.59 but sourceUrl=null
  *current:* `10.59`
- `LOW` **Coitsville Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.59 but sourceUrl=null
  *current:* `10.59`

## Columbus / Central Ohio (HIGH:0 MED:18 LOW:16)

- `MEDIUM` **Columbus** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gahanna** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gahanna** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.927¢ but currentRate=11.162, previousRate=9.756
  *current:* `10.927`
- `MEDIUM` **Grove City** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Ontario** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Dublin** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Hilliard** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Worthington** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Reynoldsburg** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **New Albany** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Bexley** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Grandview Heights** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Westerville** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['AEP Ohio']
  *current:* `['AEP Ohio']`
- `MEDIUM` **Lancaster** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Delaware (City)** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Pickerington** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Heath / Newark** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Marysville** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `LOW` **Columbus** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Gahanna** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Grove City** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.97 but sourceUrl=null
  *current:* `10.97`
- `LOW` **Ontario** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=8.66 but sourceUrl=null
  *current:* `8.66`
- `LOW` **Dublin** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Hilliard** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Worthington** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Reynoldsburg** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **New Albany** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Bexley** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Grandview Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Lancaster** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Delaware (City)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Pickerington** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Heath / Newark** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Marysville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`

## Dayton / Miami Valley (HIGH:0 MED:21 LOW:5)

- `MEDIUM` **Beavercreek** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Huber Heights** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Miamisburg** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springboro** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Xenia** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Franklin** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springfield** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Urbana** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Centerville** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Vandalia** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Dayton** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Dayton** `RATE_CHANGE_NO_PREV`  
  rateChange=22.7% set but previousRate=null
  *current:* `22.7`
- `MEDIUM` **Dayton** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.691¢ but currentRate=8.71, previousRate=None
  *current:* `10.691`
- `MEDIUM` **Dayton** `COPY_RATE_MISMATCH`  
  hook mentions 10.69¢ but currentRate=8.71, previousRate=None
  *current:* `10.69`
- `MEDIUM` **Riverside** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Fairborn** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Troy** `STALE_RENEWAL`  
  rollover termEnd=2025-12-31 expired 296d ago — any new contract?
  *current:* `2025-12-31`
- `MEDIUM` **Troy** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='no_aggregation_verified'
  *current:* `None → 2025-12-31`
- `MEDIUM` **Troy** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Middletown** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Kettering** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `LOW` **Dayton** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=8.71 but sourceUrl=null
  *current:* `8.71`
- `LOW` **Dayton** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Riverside** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.333 but sourceUrl=null
  *current:* `9.333`
- `LOW` **Riverside** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Fairborn** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.04 but sourceUrl=null
  *current:* `9.04`

## Cincinnati / SW Ohio (HIGH:12 MED:79 LOW:10)

- `HIGH` **Golf Manor** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Wayne Township (Warren Co)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Batavia Township** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Pierce Township / Amelia** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Williamsburg** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Seven Mile** `STALE_RENEWAL`  
  rollover termEnd=2025-09-30 expired 388d ago — any new contract?
  *current:* `2025-09-30`
- `HIGH` **Seven Mile** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Oxford Township (Butler Co)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Madison Township (Butler Co)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Lemon Township** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Cheviot** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Madeira** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Sharonville** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Reading** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Norwood** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Norwood** `COPY_RATE_MISMATCH`  
  takeaway mentions 7.03¢ but currentRate=10.39, previousRate=6.67
  *current:* `7.03`
- `MEDIUM` **Cincinnati** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **West Chester Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Mason** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Blue Ash** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Montgomery** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Anderson Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Anderson Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Anderson Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.86, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Anderson Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.86, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Fairfield** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Fairfield** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Fairfield** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.39, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Milford** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Loveland** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Loveland** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Loveland** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.07, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Springdale** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.29, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Springdale** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.29, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Kenwood / Symmes Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Colerain Township** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Colerain Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Colerain Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.36, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Colerain Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.36, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Delhi Township** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Delhi Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Delhi Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.32, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Forest Park** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Forest Park** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Silverton** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Silverton** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Clearcreek Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Clearcreek Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Hamilton Township (Warren Co)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.2, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Sycamore Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sycamore Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=10.21, previousRate=9.23
  *current:* `10.7`
- `MEDIUM` **Springfield Township (Hamilton Co)** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springfield Township (Hamilton Co)** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=10.29, previousRate=9.45
  *current:* `10.7`
- `MEDIUM` **Green Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Lockland** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Union Township (Clermont Co)** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Miami Township (Clermont Co)** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Golf Manor** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Waynesville** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Waynesville** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Waynesville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.14, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Waynesville** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.14, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Franklin** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **South Lebanon** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Turtlecreek Township** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Wayne Township (Warren Co)** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Springboro** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Morrow** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Batavia Township** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Pierce Township / Amelia** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Williamsburg** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Tate Township** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Goshen Township** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **New Richmond** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Oxford** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 115d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Oxford** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Seven Mile** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=None, previousRate=6.23
  *current:* `10.7`
- `MEDIUM` **Seven Mile** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=None, previousRate=6.23
  *current:* `10.7`
- `MEDIUM` **Harrison** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.24, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Harrison** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.24, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Monroe** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Oxford Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Madison Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Lemon Township** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Trenton** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Cheviot** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Madeira** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Mount Healthy** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Miami Township (Hamilton Co)** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **St. Bernard** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Morgan Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (142d ago)
  *current:* `2026-06-03`
- `LOW` **Sharonville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.39 but sourceUrl=null
  *current:* `9.39`
- `LOW` **Reading** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.29 but sourceUrl=null
  *current:* `10.29`
- `LOW` **Norwood** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.39 but sourceUrl=null
  *current:* `10.39`
- `LOW` **Cincinnati** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.44 but sourceUrl=null
  *current:* `10.44`
- `LOW` **Deer Park** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Hamilton Township (Warren Co)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.2 but sourceUrl=null
  *current:* `9.2`
- `LOW` **Hamilton Township (Warren Co)** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Liberty Township (Butler Co)** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Tate Township** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **Seven Mile** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`

## Greater Toledo (HIGH:0 MED:13 LOW:25)

- `MEDIUM` **Toledo** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Perrysburg** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Maumee** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Sylvania** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Oregon** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Lucas County Unincorporated** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Rossford** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Northwood** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Waterville** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Whitehouse** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Holland** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Jerusalem Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Washington Township (Wood)** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `LOW` **Toledo** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Toledo** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Perrysburg** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Perrysburg** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Maumee** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Maumee** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Sylvania** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Sylvania** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Oregon** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Oregon** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Lucas County Unincorporated** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Rossford** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Rossford** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Northwood** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Northwood** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Waterville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Waterville** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Whitehouse** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Whitehouse** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Holland** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Holland** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Jerusalem Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Jerusalem Township** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`
- `LOW` **Washington Township (Wood)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Washington Township (Wood)** `STALE_60`  
  lastVerified=2026-08-19 (65d ago)
  *current:* `2026-08-19`

## NW & Central Ohio (HIGH:0 MED:15 LOW:0)

- `MEDIUM` **Findlay** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Lima** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Fremont** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Tiffin** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Defiance** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sandusky** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Port Clinton** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Bucyrus** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Kenton** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Bellefontaine** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Washington Court House** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Wilmington** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Ashland** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Marion** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Fostoria** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`

## Eastern Ohio (HIGH:0 MED:10 LOW:0)

- `MEDIUM` **Zanesville** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Cambridge** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Athens / Ohio University Area** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Chillicothe** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Circleville** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Logan** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gallipolis** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Portsmouth** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Ironton** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Jackson** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`

## Municipal Utilities (HIGH:0 MED:4 LOW:1)

- `MEDIUM` **Cleveland Public Power** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Columbus Division of Power** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Piqua** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['AES Ohio']
  *current:* `['AES Ohio']`
- `MEDIUM` **Hamilton** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `LOW` **Cleveland Public Power** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`

## Electric Cooperatives (HIGH:0 MED:4 LOW:0)

- `MEDIUM` **Darke Rural Electric** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['AES Ohio']
  *current:* `['AES Ohio']`
- `MEDIUM` **Holmes-Wayne Electric** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Mid-Ohio Energy** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **South Central Power** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['AEP Ohio']
  *current:* `['AEP Ohio']`

## Other Ohio Markets (HIGH:0 MED:17 LOW:5)

- `MEDIUM` **Brunswick** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Medina City** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Elyria** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Lorain (City)** `STALE_60`  
  lastVerified=2026-06-04 (141d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Struthers** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Poland Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 145d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Poland Township** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Licking County / Pataskala** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Grove City Area / Southwest Franklin County** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Athens County (Rural AEP)** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Guernsey / Noble / Morgan Counties** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Medina County (Rural Unincorporated)** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='address_dependent'
  *current:* `2026-05-01 → 2028-06-30`
- `MEDIUM` **Medina County (Rural Unincorporated)** `STALE_60`  
  lastVerified=2026-05-01 (175d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Lakeview / Indian Lake Area** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Steubenville** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Marietta** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `MEDIUM` **McConnelsville / Morgan County** `STALE_60`  
  lastVerified=2026-06-01 (144d ago)
  *current:* `2026-06-01`
- `LOW` **Brunswick** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Medina City** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.5 but sourceUrl=null
  *current:* `9.5`
- `LOW` **Lorain (City)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.999 but sourceUrl=null
  *current:* `9.999`
- `LOW` **Licking County / Pataskala** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Grove City Area / Southwest Franklin County** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.97 but sourceUrl=null
  *current:* `10.97`

## Documentation (HIGH:0 MED:0 LOW:2)

- `LOW` **CLAUDE.md** `DOC_COUNT_MISMATCH`  
  CLAUDE.md claims 251 zones but actual=327
  *current:* `claimed=251 actual=327`
- `LOW` **CLAUDE.md** `DOC_COUNT_MISMATCH`  
  CLAUDE.md claims 18 JSON files but actual=19
  *current:* `claimed=18 actual=19`

---
*Generated by scripts/daily_audit.py — 2026-10-23*
