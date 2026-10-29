# Swiss Ephemeris fix and maths verification — Business Muhurtham

Date: 2026-10-29 · Applies to `index.html` in this repository. Reproduce with `verify/compare.py` (needs `pip install pyswisseph`).

The live site at businessmuhurtham.bharatheyavasthujyothishapadanasala.com ran the pre-fix code when this was written.

## 1. Why Swiss Ephemeris never loaded (live site shows "Fallback Active")

There were four separate faults. Any one of them on its own was enough to break it.

| # | Fault | Fix |
|---|---|---|
| 1 | `import("https://cdn.jsdelivr.net/npm/swisseph-wasm/+esm")` has no pinned version, and the `+esm` bundle can't find its `.wasm`/`.data` files | Import the pinned `swisseph-wasm@0.1.0/src/swisseph.js` (bundles Swiss Ephemeris 2.10.03) |
| 2 | The code called `mod.default.init()`, which doesn't exist | `new mod.default()` then `await inst.initSwissEph()` |
| 3 | The code used the C-style names `swe_julday`, `swe_calc_ut`, `swe_houses` and `swe_get_ayanamsa_ut`. The wrapper exposes `julday`, `calc_ut`, `houses` and `get_ayanamsa_ut` | Switched to the wrapper names. `houses().ascmc[0]` is the tropical Asc, and ayanamsa is subtracted from it |
| 4 | The page CSP `script-src` blocks WebAssembly compilation | Added `'wasm-unsafe-eval'`. This is narrower than `'unsafe-eval'`. The server's own CSP header is only `upgrade-insecure-requests`, so the meta tag decides |
| + | `SEFLG_SIDEREAL` was set to 64, which is actually `SEFLG_NONUT`. Even a loaded engine would have returned **tropical** positions | Set to 65536, combined with `SEFLG_SWIEPH` |

After the fix, the browser loads the engine with status `READY_SWISSEPH`, library version 2.10.03, and the button reads "🪐 Engine: SwissEph AGPL (Default)".

## 2. Verification against pyswisseph 2.10.03 (local, Lahiri, Moshier/SWIEPH)

Nine cases, 1950–2050: Chennai, Delhi, Trivandrum, London, Mumbai, New York, Kochi, Sydney and Bengaluru, covering IST, UTC, negative and southern-hemisphere timezones. To re-run: `python verify\compare.py verify\app_output_fixed.json`. Raw output is in `verify\results_*.txt`.

Max |app − pyswisseph| in degrees:

| Engine | Ayan | Lagna | Sun | Moon | Mer | Ven | Mars | Jup | Sat | Rahu |
|---|---|---|---|---|---|---|---|---|---|---|
| **SwissEph mode (fixed)** | 0.0000 | 0.0000 | 0.0000 | 0.0005 | 0.0000 | 0.0000 | 0.0001 | 0.0001 | 0.0001 | 0.0000 |
| Internal fallback, **before** | 0.0014 | 0.0091 | 0.011 | 0.25 | **27.2** | **78.3** | **43.6** | **11.4** | **5.4** | **125.0** |
| Internal fallback, **after** | 0.0014 | 0.0091 | 0.011 | 0.002 | 0.010 | 0.007 | 0.019 | 0.093 | 0.163 | 0.0014 |

Sunrise and sunset: before, the app used a fixed 06:15/18:15, which was wrong by up to 43 min in India and 2 h in London. After, the app's times are within **0.4 min** of `swe.rise_trans` (upper limb with refraction).

With the fix, no tithi, nakshatra, pada, yoga, karana or lagna-sign values differed in any test case, in either mode.

## 3. Bugs fixed in the internal logic

1. **Rahu/Ketu were off by 125°.** The mean-node formula was missing its 125.0445° base term. Fixed with Meeus 47.7.
2. **Mercury and Venus** were "Sun ± sine", with errors up to 78°. **Mars, Jupiter and Saturn** used heliocentric mean longitudes, with errors up to 44°. They are replaced with JPL Keplerian elements, converted to geocentric positions with light-time, precession and ΔT.
3. **The Moon** used only 6 terms, with errors up to 0.25°. That's enough to flip a nakshatra pada. Now it uses 50 Meeus terms plus ΔT.
4. **Rahu Kalam, Gulika and Yamagandam** assumed sunrise at 06:15 and a 12 h day. They now use the real sunrise and sunset for the business place and date (`getSunriseSunset`). Also fixed in the Internal Logic Audit modal.
5. **KP negation check** used string matching, so `"12".includes("2")` counted house 12 as house 2. It now compares house numbers.
6. **Date parsing.** `new Date("YYYY-MM-DD")` parses as UTC, so `getDay()`/`getDate()` shifted by a day for users west of UTC. It now parses as a local date, and day stepping is DST-safe.
7. **The audit modal** used the business-place timezone for the promoter's birth time. It now uses the birth-place timezone, matching the main engine.
8. The fallback banner claimed "±0.05°". It now states the measured accuracy.

The rule tables themselves were checked and are correct: Rahu, Gulika and Yamagandam octants by weekday, Tara cycle (Vadha = 7th), KP Vimshottari sub-lord spans, Kollam month mapping, BaZi day branch (JD 2451545 → 午), and the ascendant formula.

## 4. What changes for users

For the same input (2–16 Nov 2026, default places), the **live site returns 13 candidates and the fixed version returns 2**. The fixed version gives the same result in SwissEph and internal modes. Most of the 11 dropped slots passed on the live site only because planets were in the wrong places. For example, on 4 Nov 2026 at 09:20 the true Mars is at 116° (Kataka, the 8th house from the Dhanu lagna), so the Ashtama-shuddhi veto applies. The old code put Mars at 77° (Mithuna).

## 5. Rule refinements (second pass)

Each item was an open issue in the first pass. All are now fixed and checked with `verify/compare_rules.py` (results in `verify/results_rules.txt`).

| Item | Before | Now | Check vs pyswisseph |
|---|---|---|---|
| Sunrise convention | Upper limb + refraction only | Step 2 setting: upper limb + refraction (default) or disc centre without refraction | Disc centre within 0.1 min |
| KP 10th cusp | Asc + 270° (equal houses) | Placidus 10th cusp, i.e. the Midheaven (`houses().ascmc[1]` in SwissEph mode; `tan λ = tan RAMC / cos ε` internally) | SwissEph exact; internal ≤ 0.005° |
| Tara bala | Only Vadha (7) vetoed | Muhurta Chintamani paryaya rule. 1st cycle: Vipat (3), Pratyak (5) and Vadha (7) rejected. 2nd/3rd cycle: only Vipat pada 1, Pratyak pada 4 and Vadha pada 3 rejected; other padas amber (−6 / −6 / −10). Janma amber (−8 / −5). The override now covers all three | Rule table unit-checked for all 108 combinations |
| Void-of-course Moon | Moon ≥ 27° in sign | True Western VoC with tropical signs: no Ptolemaic aspect (0/60/90/120/180°) to Sun–Saturn perfects before the Moon leaves its sign | 80/80 samples agree with a 5-minute step search |
| Combustion | Flat 8.5° | Surya Siddhanta orbs: Mercury 14°, Venus 10°, Mars 17°, Jupiter 11°, Saturn 15° | — |
| Masa Sankramana | Sun within ±0.5° of a sign boundary | Within 16 ghatikas (6 h 24 min) of the computed Sankranti | Ingress times: SwissEph 0.01 min, internal ≤ 19 min |
| Kollam date | `floor(Sun°) + 1` | The month starts on the Sankranti day if the ingress is within the first 3/5 of daytime, otherwise the next day; the day number counts from there | Medam 1 = 14 Apr 2025 (Vishu) and Chingam 1 = 17 Aug 2025 match the published calendar |
| Zero coordinates | `parseFloat(...) \|\| default` dropped tz/lat/lon of 0 | `attrNum()` keeps any finite value | — |
| Offline engine | jsDelivr only | `vendor/swisseph-wasm/` (0.1.0, SHA-256 checked against jsDelivr) loads first; the CDN is the fallback | Browser loads only the vendored files |
| `.exe` | Embedded old `index.html` | Rebuilt by CI from this `index.html` | Build pipeline 15/15 locally |

The Tara rule came from a specialist review of Muhurta Chintamani, Muhurta Martanda, Kalaprakasika and B.V. Raman's *Muhurtha*. That review was done from knowledge of the texts, not checked against a printed edition.

**`.exe` limitation:** the launcher opens the page as a `file://` URL, and browsers won't load ES modules or WebAssembly from `file://`. The `.exe` therefore uses the CDN copy when online and the internal engine when offline. A web deployment over http(s) uses the vendored copy and works offline.

**Swiss Ephemeris licence:** the library is dual-licensed by Astrodienst (AGPL-3.0 or commercial). The `swisseph-wasm` wrapper is GPL-3.0-or-later. This repository is AGPL-3.0 and public, which satisfies the AGPL option. A closed-source or modified deployment that isn't published would need Astrodienst's commercial licence.

## 6. Scoring model v2 (spreading out the 99% scores)

**Problem.** The old score was 70 plus up to about +58 in bonuses, capped at 99. Almost every slot that passed the vetoes showed 99%, so there was nothing to choose between.

**New model.** The model comes from a specialist review of Muhurta Chintamani, Muhurta Martanda, Kalaprakasika and Raman's *Muhurtha*. The integer point values are a calibrated synthesis, not figures quoted from one text.

- **New vetoes** (overridable in Step 2 via "Omit Panchanga Vetoes"): Amavasya, Vishti (Bhadra) karana, Vyatipata and Vaidhriti yogas, and Chandrashtama.
- **New points:**
  - Tithi: Rikta and late Krishna tithis are penalised.
  - Weekday: Wednesday, Thursday and Friday are best for commerce.
  - Nakshatra class: Kshipra and Dhruva +10, down to Tikshna −12.
  - Yoga: including partial yogas, which are bad only in their first ghatikas.
  - Karana: Vanija +4.
  - Chandrabala.
  - Lagna sign nature: fixed signs best.
  - Planets by house from lagna, capped at −15 to +20.
  - Lagna at a sign edge (sandhi).
  - Paksha bala.
- **Existing bonuses re-weighted:** Tara ×0.4, Ashtama +4, karaka +8, KP +5, Western +3, QMDJ +3. The base of 70 is gone.
- **Display score:** `clamp(round(50 + raw × 5/6), 1, 99)` on a fixed scale, so a score means the same thing in every search. Grades: Excellent ≥ 85, Good 70–84, Fair 55–69, Weak < 55.
- **Ties** are broken by Chandrabala, then Nakshatra, then Tithi.

**Result** (Trivandrum, default promoter):

| Search | Slots | At 99 before | At 99 now | Distinct scores | Range |
|---|---|---|---|---|---|
| 2 Nov – 15 Dec 2026 | 11 | most | 0 | 11 | 63–95 |
| Jan – Mar 2027 | 19 | most | 1 | 14 | 32–99 |

**Check.** Tithi, yoga and karana indices and the Panchanga veto detection match pyswisseph for all 26 slots of a Nov 2026 – Jan 2027 search with vetoes omitted (`verify/compare_panchanga.py`, `verify/results_panchanga.txt`).

## 7. Notes

- pyswisseph had no `.se1` files, so the reference ran in Moshier mode (about 1″). That is well inside every tolerance used here.
