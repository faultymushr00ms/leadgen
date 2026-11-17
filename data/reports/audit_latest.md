# FORGE Daily Audit — 2026-11-17

**346 findings** | HIGH: 44  MEDIUM: 234  LOW: 68
Zones checked: 456 | Elapsed: 0.01s

## ✅ No new findings since 2026-11-16

*(No previous report to diff against.)*

## NE Ohio / Cleveland / NOPEC (HIGH:5 MED:39 LOW:9)

- `HIGH` **East Cleveland** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Plain Township** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Paris Township (Stark)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Bay Village** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Hubbard** [gas] `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Lakewood** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.399¢ but currentRate=10.599, previousRate=None
  *current:* `10.399`
- `MEDIUM` **Lakewood** `COPY_RATE_MISMATCH`  
  hook mentions 10.399¢ but currentRate=10.599, previousRate=None
  *current:* `10.399`
- `MEDIUM` **Strongsville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Mentor** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Chardon / Geauga County** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.399¢ but currentRate=10.399, previousRate=9.999
  *current:* `9.399`
- `MEDIUM` **Chardon / Geauga County** `COPY_RATE_MISMATCH`  
  hook mentions 9.399¢ but currentRate=10.399, previousRate=9.999
  *current:* `9.399`
- `MEDIUM` **Niles** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Girard** `STALE_RENEWAL`  
  rollover termEnd=2025-12-31 expired 321d ago — any new contract?
  *current:* `2025-12-31`
- `MEDIUM` **Girard** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Boardman Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Canfield** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.98¢ but currentRate=8.66, previousRate=None
  *current:* `9.98`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.39¢ but currentRate=8.66, previousRate=None
  *current:* `10.39`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  hook mentions 9.98¢ but currentRate=8.66, previousRate=None
  *current:* `9.98`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  hook mentions 10.39¢ but currentRate=8.66, previousRate=None
  *current:* `10.39`
- `MEDIUM` **Salem** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Alliance** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Mansfield** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Coshocton** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Massillon** `COPY_RATE_MISMATCH`  
  takeaway mentions 8.5¢ but currentRate=10.399, previousRate=8.999
  *current:* `8.5`
- `MEDIUM` **Perry Township (Stark)** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Andover** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Westlake** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.11¢ but currentRate=None, previousRate=8.38
  *current:* `10.11`
- `MEDIUM` **Shaker Heights** `COPY_RATE_MISMATCH`  
  hook mentions 10.399¢ but currentRate=9.99, previousRate=None
  *current:* `10.399`
- `MEDIUM` **Olmsted Falls** `COPY_RATE_MISMATCH`  
  takeaway mentions 6.5¢ but currentRate=10.399, previousRate=9.999
  *current:* `6.5`
- `MEDIUM` **Twinsburg** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Parma Heights** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.19¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.19`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.11¢ but currentRate=10.399, previousRate=9.999
  *current:* `11.11`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  hook mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  hook mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Amherst** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Grafton** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Painesville** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Madison Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Bainbridge Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Newbury Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `LOW` **Canfield** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Wooster** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **New Philadelphia / Tuscarawas County** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **Jackson Township (Stark)** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Perry Township (Stark)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.99 but sourceUrl=null
  *current:* `9.99`
- `LOW` **Andover** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.86 but sourceUrl=null
  *current:* `9.86`
- `LOW` **Akron** [gas] `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Youngstown** [gas] `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Warren** [gas] `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`

## Ashtabula County (HIGH:0 MED:27 LOW:0)

- `MEDIUM` **Ashtabula Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Geneva Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Harpersfield Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Jefferson Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Kingsville Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Plymouth Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Saybrook Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Andover Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Austinburg Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Cherry Valley Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Colebrook Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Denmark Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Dorset Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Hartsgrove Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Lenox Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Monroe Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Morgan Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **New Lyme Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Orwell Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Pierpont Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Richmond Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Rome Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Sheffield Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Trumbull Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Wayne Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Williamsfield Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Windsor Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`

## Akron / Canton (HIGH:1 MED:10 LOW:2)

- `HIGH` **Stark County (Unincorporated / Remaining)** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Akron** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Akron** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.95¢ but currentRate=9.24, previousRate=None
  *current:* `9.95`
- `MEDIUM` **Akron** `COPY_RATE_MISMATCH`  
  hook mentions 9.95¢ but currentRate=9.24, previousRate=None
  *current:* `9.95`
- `MEDIUM` **Green** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  hook mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  hook mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Medina County** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Stark County (Unincorporated / Remaining)** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='no_aggregation_verified'
  *current:* `2025-08-01 → 2026-08-31`
- `LOW` **Green** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Medina County** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.5 but sourceUrl=null
  *current:* `9.5`

## Youngstown / Warren (HIGH:0 MED:17 LOW:6)

- `MEDIUM` **Youngstown** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  hook mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  hook mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Trumbull County** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Mahoning County** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='unresolved'
  *current:* `2026-06-01 → 2027-12-01`
- `MEDIUM` **Mahoning County** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Warren City** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.999¢ but currentRate=10.399, previousRate=None
  *current:* `9.999`
- `MEDIUM` **Howland Township** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Brookfield Township (Trumbull)** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Weathersfield Township** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Vienna Township** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Champion Township** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Bazetta Township** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Campbell** `STALE_60`  
  lastVerified=2026-06-04 (166d ago)
  *current:* `2026-06-04`
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

## Columbus / Central Ohio (HIGH:7 MED:4 LOW:8)

- `HIGH` **Dublin** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Hilliard** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Bexley** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Grandview Heights** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Pickerington** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Heath / Newark** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Marysville** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Columbus** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gahanna** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gahanna** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.927¢ but currentRate=11.162, previousRate=9.756
  *current:* `10.927`
- `MEDIUM` **Grove City** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
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
- `LOW` **Bexley** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Grandview Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`

## Dayton / Miami Valley (HIGH:0 MED:22 LOW:4)

- `MEDIUM` **Beavercreek** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Huber Heights** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Miamisburg** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Miamisburg** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Xenia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=None, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Xenia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=None, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Urbana** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Centerville** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Centerville** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Vandalia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Vandalia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Dayton** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
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
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Fairborn** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=None
  *current:* `11.53`
- `MEDIUM` **Fairborn** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=None
  *current:* `11.73`
- `MEDIUM` **Troy** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=6.57
  *current:* `11.53`
- `MEDIUM` **Troy** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=6.57
  *current:* `11.73`
- `MEDIUM` **Kettering** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=None
  *current:* `11.53`
- `MEDIUM` **Kettering** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=None
  *current:* `11.73`
- `LOW` **Dayton** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=8.71 but sourceUrl=null
  *current:* `8.71`
- `LOW` **Dayton** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Riverside** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.333 but sourceUrl=null
  *current:* `9.333`
- `LOW` **Riverside** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`

## Cincinnati / SW Ohio (HIGH:12 MED:73 LOW:9)

- `HIGH` **Sharonville** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Golf Manor** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Wayne Township (Warren Co)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Batavia Township** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Williamsburg** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Seven Mile** `STALE_RENEWAL`  
  rollover termEnd=2025-09-30 expired 413d ago — any new contract?
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
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sharonville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.276¢ but currentRate=None, previousRate=9.39
  *current:* `10.276`
- `MEDIUM` **Reading** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Norwood** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Norwood** `COPY_RATE_MISMATCH`  
  takeaway mentions 7.03¢ but currentRate=10.39, previousRate=6.67
  *current:* `7.03`
- `MEDIUM` **Cincinnati** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **West Chester Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Mason** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Blue Ash** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Montgomery** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Anderson Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Anderson Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Anderson Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.86, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Anderson Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.86, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Fairfield** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Fairfield** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Fairfield** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.39, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Milford** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springdale** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Kenwood / Symmes Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Colerain Township** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Colerain Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Colerain Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.36, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Colerain Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.36, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Delhi Township** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Delhi Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Delhi Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.32, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Forest Park** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Forest Park** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Silverton** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Silverton** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Clearcreek Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Clearcreek Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Deer Park** `STALE_RENEWAL`  
  rollover termEnd=2026-07-31 expired 109d ago — any new contract?
  *current:* `2026-07-31`
- `MEDIUM` **Hamilton Township (Warren Co)** `STALE_RENEWAL`  
  rollover termEnd=2026-07-31 expired 109d ago — any new contract?
  *current:* `2026-07-31`
- `MEDIUM` **Hamilton Township (Warren Co)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.2, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Liberty Township (Butler Co)** `STALE_RENEWAL`  
  rollover termEnd=2026-07-31 expired 109d ago — any new contract?
  *current:* `2026-07-31`
- `MEDIUM` **Mariemont** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sycamore Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sycamore Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=10.21, previousRate=9.23
  *current:* `10.7`
- `MEDIUM` **Springfield Township (Hamilton Co)** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springfield Township (Hamilton Co)** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=10.29, previousRate=9.45
  *current:* `10.7`
- `MEDIUM` **Green Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Lockland** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Union Township (Clermont Co)** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Miami Township (Clermont Co)** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Golf Manor** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **South Lebanon** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Turtlecreek Township** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Wayne Township (Warren Co)** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Morrow** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Batavia Township** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Williamsburg** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Tate Township** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Goshen Township** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **New Richmond** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Oxford** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 140d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Oxford** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Seven Mile** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=None, previousRate=6.23
  *current:* `10.7`
- `MEDIUM` **Seven Mile** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=None, previousRate=6.23
  *current:* `10.7`
- `MEDIUM` **Harrison** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Monroe** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Oxford Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Madison Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Lemon Township** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Trenton** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Wyoming** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Cheviot** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Madeira** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Mount Healthy** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Miami Township (Hamilton Co)** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **St. Bernard** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Morgan Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (167d ago)
  *current:* `2026-06-03`
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
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Hamilton Township (Warren Co)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.2 but sourceUrl=null
  *current:* `9.2`
- `LOW` **Hamilton Township (Warren Co)** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Liberty Township (Butler Co)** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Tate Township** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **Seven Mile** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`

## Greater Toledo (HIGH:1 MED:12 LOW:22)

- `HIGH` **Washington Township (Wood)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Toledo** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Perrysburg** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Maumee** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Sylvania** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Oregon** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Lucas County Unincorporated** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Rossford** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Northwood** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Waterville** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Whitehouse** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Holland** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Washington Township (Wood)** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.09¢ but currentRate=None, previousRate=8.63
  *current:* `11.09`
- `LOW` **Toledo** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Toledo** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Perrysburg** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Perrysburg** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Maumee** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Maumee** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Sylvania** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Sylvania** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Oregon** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Oregon** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Lucas County Unincorporated** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Rossford** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Rossford** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Northwood** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Northwood** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Waterville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Waterville** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Whitehouse** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Whitehouse** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Holland** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Holland** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`
- `LOW` **Washington Township (Wood)** `STALE_60`  
  lastVerified=2026-08-19 (90d ago)
  *current:* `2026-08-19`

## NW & Central Ohio (HIGH:1 MED:8 LOW:1)

- `HIGH` **Tiffin** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Lima** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Fremont** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Defiance** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sandusky** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Port Clinton** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Kenton** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Wilmington** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Ashland** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `LOW` **Bucyrus** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`

## Eastern Ohio (HIGH:1 MED:10 LOW:0)

- `HIGH` **Chillicothe** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Zanesville** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Cambridge** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Athens / Ohio University Area** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Chillicothe** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Circleville** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Logan** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gallipolis** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Portsmouth** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Ironton** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Jackson** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`

## Municipal Utilities (HIGH:13 MED:1 LOW:1)

- `HIGH` **Cleveland Public Power** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Columbus Division of Power** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Wellsville** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Cortland** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Liberty Center** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Hamler** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **West Unity** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Stryker** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Wauseon** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Coldwater** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Delphos** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Hamilton** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Ada** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Piqua** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['AES Ohio']
  *current:* `['AES Ohio']`
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

## Other Ohio Markets (HIGH:3 MED:7 LOW:4)

- `HIGH` **Licking County / Pataskala** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Athens County (Rural AEP)** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `HIGH` **Guernsey / Noble / Morgan Counties** `STALE_60`  
  lastVerified=2026-05-01 (200d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Medina City** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Struthers** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Poland Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 170d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Poland Township** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Steubenville** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Marietta** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `MEDIUM` **McConnelsville / Morgan County** `STALE_60`  
  lastVerified=2026-06-01 (169d ago)
  *current:* `2026-06-01`
- `LOW` **Crosby Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.88 but sourceUrl=null
  *current:* `9.88`
- `LOW` **Medina City** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.5 but sourceUrl=null
  *current:* `9.5`
- `LOW` **Licking County / Pataskala** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Russells Point** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.26 but sourceUrl=null
  *current:* `9.26`

## Documentation (HIGH:0 MED:0 LOW:2)

- `LOW` **CLAUDE.md** `DOC_COUNT_MISMATCH`  
  CLAUDE.md claims 251 zones but actual=427
  *current:* `claimed=251 actual=427`
- `LOW` **CLAUDE.md** `DOC_COUNT_MISMATCH`  
  CLAUDE.md claims 18 JSON files but actual=20
  *current:* `claimed=18 actual=20`

---
*Generated by scripts/daily_audit.py — 2026-11-17*
