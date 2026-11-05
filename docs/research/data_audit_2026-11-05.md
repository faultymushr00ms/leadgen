# Data factuality audit — 2026-11-05

Automated read-only review of `data/regions/*.json` (427 zones). No zone data was changed: nothing here is *proven* incorrect, so under the History rules nothing was deleted. These are items needing verification.

## Summary
- 83 of 311 zones with a `currentRate` have no `sourceUrl` (62 last verified before 2026-08).
- 51 zones are `confidence: high` with no `sourceUrl` (mostly NOAC/Toledo, SOPEC suburbs, Trumbull/Mahoning, Dayton, Columbus, 20 municipal utilities).
- Time-stale statuses as of today: 20 zones are `pain_coming` with a `termStart` already past; 2 have an expired `termEnd` but still read `stable` (Cincinnati 2026-11-01, Stark County unincorporated 2026-08-31).
- Round-number unsourced `previousRate` values (placeholder-like): see list below.
- `Westerville` has no `lastVerified`; `Heath / Newark` and `Mahoning County` are `aggregationStatus: unresolved`.
- CLAUDE.md counts are out of date: municipal file has 48 zones (doc says 47; schema list says 36 muni-status), co-ops 24 (doc also says "25" elsewhere).
- 8 co-op zones lack `futureUse: municipal_blacklist` (Butler Rural, Darke Rural, Frontier Power, Holmes-Wayne, LMRE, North Central, Pioneer, Midwest Energy & Communications).
- Rate-change math: stored `rateChange` agrees with computed values everywhere checked.

## Flagged rows (type, file, zone, value)
```
EXPIRED akron_summit_medina Stark County (Unincorporated / Remaining) 2026-08-31 stable
STALE_PC cincinnati_duke Reading 2026-06-01
STALE_PC cincinnati_duke Norwood 2026-06-01
EXPIRED cincinnati_duke Cincinnati 2026-11-01 stable
STALE_PC columbus_aep Columbus 2026-06-01
STALE_PC columbus_aep Gahanna 2026-06-01
STALE_PC columbus_aep Grove City 2026-07-01
STALE_PC dayton_aes_suburbs Miamisburg 2026-01
STALE_PC dayton_aes_suburbs Centerville 2026-01
STALE_PC dayton_aes_suburbs Vandalia 2026-01
STALE_PC dayton_sw_ohio Fairborn 2026-01
STALE_PC dayton_sw_ohio Kettering 2026-01
STALE_PC ne_ohio_firstenergy North Canton 2026-01-01
STALE_PC ne_ohio_firstenergy Massillon 2026-06-01
STALE_PC remaining_ohio_markets Licking County / Pataskala 2026-06-01
STALE_PC sopec_columbus_suburbs Dublin 2026-06-01
STALE_PC sopec_columbus_suburbs Hilliard 2026-06-01
STALE_PC sopec_columbus_suburbs Worthington 2026-06
STALE_PC sopec_columbus_suburbs Reynoldsburg 2026-09
STALE_PC sopec_columbus_suburbs Bexley 2026-06-01
STALE_PC sopec_columbus_suburbs Grandview Heights 2026-06-01
STALE_PC sopec_columbus_suburbs Lancaster 2026-09
ROUNDPRIOR youngstown_warren Trumbull County 7.9 10.14
ROUNDPRIOR youngstown_warren Mahoning County 7.9 None
ROUNDPRIOR youngstown_warren Howland Township 7.9 10.14
ROUNDPRIOR youngstown_warren Weathersfield Township 7.9 10.14
ROUNDPRIOR youngstown_warren Vienna Township 7.9 10.14
ROUNDPRIOR youngstown_warren Champion Township 7.9 10.14
ROUNDPRIOR youngstown_warren Bazetta Township 7.9 10.14
```

Recommended: verify against PUCO / program pages, then correct status, or delete proven-wrong values with a one-line removal note (no value in note).
