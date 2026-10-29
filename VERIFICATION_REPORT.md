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

## 5. Open issues for your decision (not changed)

- **Sunrise convention:** I used the upper limb with refraction (−0.833°), which most published panchangams use. Some traditions use the disc centre without refraction, which is about 3 min later.
- **KP 10th cusp** is computed as Asc + 270° (equal houses). Classical KP uses Placidus cusps, and Swiss Ephemeris could supply them with `houses(jd, lat, lon, "P")`.
- **Tara bala** penalises only Vadha (7). Vipat (3) and Pratyak (5) are usually avoided too.
- **Heuristics labelled as rules:** VoC Moon means "Moon ≥ 27° in its sign", which is not a true void-of-course check. Combustion uses a flat 8.5° for every planet, while the classical orbs differ per planet. Masa Sankramana uses ±0.5°.
- **Kollam day** is `floor(Sun° in sign) + 1`. The Kerala civil day count actually depends on when the sankranti falls relative to sunset.
- **`parseFloat(...) || 5.5`** turns a timezone, latitude or longitude of 0 into a default value. It's harmless today, since no place option has tz 0, but it would break for UTC locations.
- **The Swiss Ephemeris engine depends on jsDelivr at runtime.** For offline or `.exe` builds, consider vendoring `swisseph-wasm@0.1.0` (its `src/` and `wasm/` folders) next to `index.html`. It is AGPL, the same as now.
- The `.exe` build in the source folder still embeds the old `index.html`.

## 6. Notes

- pyswisseph had no `.se1` files, so the reference ran in Moshier mode (about 1″). That is well inside every tolerance used here.
