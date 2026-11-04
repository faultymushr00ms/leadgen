# Data review: non-factual information — 2026-11-04

Read-only review of 427 zones in `data/regions/`. No zone data was changed; nothing was proven incorrect against a source.

## Unsourced rates (83 zones have currentRate but no sourceUrl)
- Cincinnati/Duke suburbs: flat 10.7¢ across ~14 zones.
- Eastern and NW Ohio: repeated 10.19¢ / 11.262¢ / 11.07¢, mostly low confidence.
- NOAC (Toledo area): 9.75¢ vs 8.63¢ on 11 zones.
- Trumbull/Mahoning: 10.14¢ vs 7.9¢ on 6 zones.
- SOPEC suburbs and Columbus: 11.162¢ vs 9.756¢; 10.01¢ vs 9.08¢.
- Medina County and Medina City: 9.5¢ vs 6.05¢.
- Placeholder-looking priors: 7.9 (x7), 7.0 (x3), 6.05, 6.57, 6.67. See `rate_change_disagreements.md`.

## Stale status (about 20 zones)
`pain_coming` with a start date already past: Columbus, Gahanna, Grove City, Dublin, Hilliard, Bexley, Grandview Heights, Worthington, Reynoldsburg, Lancaster, Licking County/Pataskala, Reading, Norwood, Miamisburg, Centerville, Vandalia, Fairborn, Kettering, North Canton, Massillon. Several last verified May–June 2026.

## Contradictions
- North Canton: stored 10.399¢, takeaway says the city page shows 10.499¢.
- Hamilton Township (Warren Co): stored 9.2¢, takeaway says the program expired and accounts are on Duke default 10.70¢+.

## Missing data
- Westerville: no lastVerified.

## Next step
Re-verify the unsourced and placeholder rates against PUCO, city or supplier pages. Delete values proven wrong and log a one-line removal note without the value (per CLAUDE.md).
