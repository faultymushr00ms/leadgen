# FORGE proposed changes — 2026-11-17

**Nothing in this file has been applied to `main`.** Each item needs your approval.

To approve, reply with the IDs, for example `approve P01 P03 P06` or `approve all recommended`. Approved items get applied to one clean branch from `main` and go up as one PR for you to merge. Anything rejected is marked `rejected` and not proposed again unless new evidence turns up.

Machine-readable copy with every field's old and new value: `proposed_changes_2026-11-17.json` (same folder).

## Where this came from

`main` hasn't changed since 2026-11-02 (`534104d`). Since then the daily fact-check runs have each written fixes on their own branch, and none were merged. So the same fixes were redone several times, and some disagree. This list combines them, removes the duplicates, and picks one version where they conflict:

| Branch | Date | What it holds |
|---|---|---|
| `claude/friendly-feynman-9m8r0v` (PR #16) | 11-11 | Licking/Newark, Pickerington, Marysville, Dublin, Beavercreek, Niles, Mansfield, Delhi |
| `claude/friendly-feynman-4yq6dp` | 11-12 | AES default in 3 Dayton suburbs (partly superseded, see P03–P05) |
| `claude/friendly-feynman-l8i9hm` | 11-13 | Gas layer (22 zones), Colerain/Oxford wording |
| `claude/friendly-feynman-14m79j` | 11-14 | Co-op HQs, Sharonville/Washington Twp rateChange, Stark term dates |
| `claude/friendly-feynman-u3wdxu` | 11-15 | Co-op roster, Dayton, Sharonville WGL term, Cincinnati |
| `claude/friendly-feynman-y3ofg2` | 11-17 | Dayton, Riverside, Huber Heights, Urbana |
| PR #15 `cursor/dayton-aggregation-renewal-a97f` | 11-02 | Dayton (same as P01) |

## Proposals

| ID | Change | Confidence | Recommend |
|---|---|---|---|
| **P01** | **Dayton**: the aggregation did *not* expire. It is SOPEC/AEP Energy at 10.691¢ (100% renewable) through the June 2027 meter read. Prior rate 8.71¢, +22.7%, status `pain_hit`. Removes the "expired / now on AES default / biggest shock in the state" claims. | likely | ✅ |
| **P02** | **Riverside**: same SOPEC renewal, 9.333¢ → 10.691¢ (+14.6%) to June 2027. | likely | ✅ |
| **P03** | **Beavercreek**: city aggregation on Constellation at 8.699¢ through December 2026. The city is pausing aggregation after that, so accounts go to the AES default (10.86¢). ⚠️ *Conflict:* two branches call it "no aggregation". The PR #16 version was checked against the live city page. | confirmed | ✅ PR #16 version |
| **P04** | **Huber Heights**: remove the false "AES standard hit 10.691¢ (+22.7%)" and the 8.71¢ prior. Mark it unresolved/verify. A 2025 SOPEC opt-out letter suggests a city program. ⚠️ *Alternative (4yq6dp):* set it to the AES default 10.86¢ with prior 9.45¢. | likely | ✅ verify version |
| **P05** | **Urbana**: same as P04. The Dynegy page lists 9.08¢ (Dec 2025 – May 2028), single source. | likely | ✅ verify version |
| **P06** | **Sharonville**: WGL Energy 10.276¢ from November 2026 (Dynegy 9.39¢ before, +9.4%), sourced to the city newsflash. This replaces an impossible 42.9%. | likely | ✅ |
| **P07** | **Washington Twp (Wood)**: clear rateChange 13.0. It can't come from the stored rates. | confirmed | ✅ |
| **P08** | **Stark County (Unincorporated)**: remove term dates from a record that has no program. | confirmed | ✅ |
| **P09** | **Cincinnati**: the fixed 10.44¢ term ended 2026-11-01, so the status changes from `stable` to `verify`. The successor is variable. | likely | ✅ |
| **P10** | **Co-op roster**: delete "Ohio Valley Electric Cooperative", which does not exist (OVEC is a wholesale generator). Delete the "2 Unconfirmed" placeholder. Add **Hancock-Wood Electric** and **Midwest Electric** (St. Marys). North Western Electric stays as a 1-item placeholder. | likely | ✅ |
| **P11** | **Co-op HQ/territory**: Frontier Power is in Coshocton, not NW Ohio. Tri-County is in Malinta. LMRE is in Wellington. Firelands is in New London. | likely | ✅ |
| **P12 / P12b** | **Licking County/Pataskala, Heath/Newark**: Dynegy 10.29¢, Dec 2025 – Dec 2026. The current values are Columbus's AEP 10.01¢ copied over. | confirmed | ✅ |
| **P13** | **Pickerington, Marysville**: remove the copied Columbus 9.08→10.01¢ program. No program found on any list. | likely | ✅ |
| **P14** | **Dublin**: not on the SOPEC member list. Remove 11.162¢ and mark unresolved/verify. | likely | ✅ |
| **P15** | **Niles**: municipal electric (AMP), not Ohio Edison. Moves to the do-not-sell list. | confirmed | ✅ |
| **P16** | **Mansfield**: joined NOPEC in 2026 (10.399¢ standard). It is currently marked "no aggregation". | likely | ✅ |
| **P17 / P17b** | **Delhi Twp, Colerain Twp, Oxford**: June "expires this month" wording rewritten in past tense. Oxford's Duke default becomes 10.49¢. | confirmed | ✅ |
| **P18** | **Gas layer** (not shown in the app yet): Toledo-area gas is Columbia Gas, not Dominion. Dominion was renamed Enbridge Gas Ohio in March 2024. Fixes wrong electric claims in 22 gas zones and the Settings dropdown. | confirmed | ✅ |
| **P19** | **CLAUDE.md**: the "Dayton/AES Ohio 8.71→10.691¢" line describes Dayton's SOPEC rate, not AES. The AES default went about 9.45→10.86¢ (+15%). The zone count (251 / 18 files) is now 427 / 20. The NOAC "9.75¢ through ~June 2027" line conflicts with the zone files. | confirmed | ✅ (doc only) |

Every removed value gets a one-line removal note in `data/history/removal_notes.jsonl`, without the value, per CLAUDE.md.

## Open — research needed before anything is proposed

1. **8.71¢ prior rate on Miamisburg, Centerville, Vandalia, Xenia** (MVCC zones). It is probably copied from Dayton, but there is no source either way.
2. **Duke "10.7¢"** on about 15 Cincinnati suburbs with no source. The October Duke Price to Compare is 10.49¢. Check whether these are real aggregation rates.
3. **Wellsville, Cortland**: filed as municipal utilities but tagged as Dynegy aggregations, with no source.
4. **About 20 `pain_coming` statuses** where the increase already took effect (Columbus, Gahanna, Dublin, Hilliard, Worthington, Bexley, MVCC zones…).
5. **Liberty Township (Butler)**: two electric records disagree (10.099¢ stable vs a 9.37¢ rollover).
6. **NOAC**: CLAUDE.md says 9.75¢ to ~June 2027, but the zones store a termEnd of 2026-05-31 with status rollover.
7. **51 "high confidence" records with no sourceUrl.**
8. **Network**: ohioec.org, sopec-oh.gov, daytonohio.gov and hhoh.org are blocked from these sessions. Allowing them would let runs confirm P02, P04, P05 and P10 directly.

## Housekeeping after you decide

Once the approved items are merged, the overlapping branches and PRs (#15, #16 and the six `claude/friendly-feynman-*` fix branches) are redundant. Close or delete them only when you say so.
