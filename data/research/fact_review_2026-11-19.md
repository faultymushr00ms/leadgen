Fact review, 2026-11-19

Scope: all 20 files in data/regions/ (427 records). Automated scan, then web checks
on the highest-impact claims. ohioec.org and sopec-oh.gov could not be fetched from
this session (network policy); search results quoting those pages were used instead.

Fixed in this pass

- Dayton (dayton_sw_ohio): the record said the SOPEC program expired June 30, 2026 and
  accounts went to AES standard supply "with no contract". The City of Dayton and SOPEC
  pages show a renewal at 10.691¢/kWh green (10.576¢ brown opt-down) for June 2026 to
  May 2027, supplier AEP Energy. Current set to 10.691, prior 8.71 kept as genuine
  history, takeaway/hook rewritten, sourceUrl added.
- Beavercreek, Huber Heights, Urbana (dayton_aes_suburbs): stored the Dayton SOPEC price
  pair (8.71 -> 10.691, +22.7%) as the "AES standard rate". The stored PUCO Price to
  Compare for AES Ohio (data/research/price_to_compare.json) is 10.86¢ for June 2026 to
  May 2027. Rates removed; text now cites the PUCO figure as residential.
- Sharonville (cincinnati_duke): rateChange 42.9 with no current rate; it does not match
  the zone's own figures. Removed.
- ohio_electric_cooperatives: removed "Ohio Valley Electric Cooperative" (no such co-op
  found; the name belongs to the OVEC generating company) and the "Ohio Electric
  Co-ops — 2 Unconfirmed" placeholder record.

Flagged, not changed (needs a source check)

- 27 Duke Energy Ohio zones (mostly cincinnati_duke_suburbs) state that commercial
  accounts are "on Duke default at 10.70¢". 10.7016¢ is described as the Duke PTC as of
  June 1, 2026; the stored PUCO figure for October 2026 is 10.49¢ and is residential.
  commercial_ptc.json says no Duke commercial default figure exists.
- Riverside (dayton_sw_ohio): says the SOPEC program expired and accounts went to AES
  default. Dayton's SOPEC program renewed, so this is probably wrong too. No Riverside
  source found yet.
- Miamisburg, Centerville, Vandalia, Xenia: previousRate 8.71 is Dayton's SOPEC price,
  not shown to be these communities' prior rate.
- Cincinnati (cincinnati_duke): termEnd 2026-11-01 has passed, status still "stable",
  no sourceUrl.
- Stark County (unincorporated) termEnd 2026-08-31 and Washington Township (Wood)
  termEnd 2026-05-31 have passed and the status was not updated.
- 51 records marked confidence "high" have no sourceUrl (most are municipal utilities
  where that matters less; also Columbus, Gahanna, Grove City, Westerville, Dublin,
  Hilliard, Bexley, Grandview Heights, Toledo, Perrysburg, Maumee, Medina County).
- Co-op roster: the file now has 22 Ohio co-ops plus Midwest Energy & Communications.
  Buckeye Power serves 24 Ohio co-ops. Hancock-Wood Electric and North Western Electric
  may be missing; not added until confirmed against ohioec.org.
- CLAUDE.md "Dayton/AES Ohio: 8.71¢ -> 10.691¢" describes the SOPEC Dayton program,
  not the AES Ohio default rate. That wording is where the suburb error came from.
