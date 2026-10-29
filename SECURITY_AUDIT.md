# Security & sensitive-information audit

Date: 2026-10-29 · Scope: every file in this repository at the time of the Swiss Ephemeris fix commit.

## Sensitive information

| Check | Result |
|---|---|
| API keys, tokens, private keys (GitHub, AWS, Google, OpenAI patterns, PEM blocks) | None found |
| Passwords or credentials | None found |
| Local machine paths or usernames | None. They were removed from the verification report before commit |
| Personal email addresses | None. Only the public institute contact `contact@bharatastrology.org` |
| Phone numbers / postal address | The institute's public business contacts (footer and "Institute Details"). These are intentionally public and match the live site |
| Build outputs (`.exe`, `.sha256`) | Not committed; listed in `.gitignore` and produced by CI |
| Test data in `verify/` | City coordinates and computed planet longitudes only |

## Application security (`index.html`)

| Area | Status |
|---|---|
| XSS sinks | 0 × `.innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`. Enforced by `tests/test_muhurtham_engine.js` |
| Content-Security-Policy | `default-src 'self'`. Scripts and connections allowed only from `'self'` and the pinned `cdn.jsdelivr.net/npm/swisseph-wasm@0.1.0/` path. Plus `object-src 'none'`, `base-uri 'self'`, `form-action 'self'`. `'wasm-unsafe-eval'` permits WebAssembly compilation only, not JS `eval` |
| Third-party code | One dependency: `swisseph-wasm@0.1.0` (exact version). A vendored copy in `vendor/swisseph-wasm/` loads first. All 5 files match jsDelivr's published SHA-256 hashes; `src/swisseph.js` imports only `../wasm/swisseph.js` and makes no network calls. The pinned CDN copy is a fallback |
| External links | All `target="_blank"` links carry `rel="noopener noreferrer"`; `window.open` uses `noopener,noreferrer` |
| Local storage | Form data (name, birth date/time/place, business details) is autosaved to `localStorage` in the user's own browser only. Nothing is sent to any server. It is restored via `.value` assignment, so there is no HTML injection |
| Network | No analytics, trackers or form submissions. The only network fetch is the Swiss Ephemeris module and its `.wasm`/`.data` files |

## Build & CI

| Area | Status |
|---|---|
| Workflow permissions | `contents: read` (least privilege) |
| Actions | `actions/checkout@v4`, `setup-node@v4`, `upload-artifact@v4`. These are first-party, pinned to major tags |
| Build scripts | Compile with the local .NET `csc.exe`; no downloads or `Invoke-Expression`. `-ExecutionPolicy Bypass` is scoped to the repo's own scripts |

## Recommendations (not yet applied)

1. ~~Vendor `swisseph-wasm@0.1.0`~~: **done** (see above). The CDN fallback remains for `file://` launches (the `.exe`). Once only http(s) hosting is used, `https://cdn.jsdelivr.net/...` can be dropped from the CSP and the loader.
2. **Pin GitHub Actions to commit SHAs** instead of `@v4` tags, for supply-chain hardening.
3. **Privacy notice:** tell users that birth details are kept in their browser's local storage, and offer a "clear saved data" button.
4. `'unsafe-inline'` remains in `script-src` because the app is a single inline-script file. Moving the script to a separate `.js` file would allow removing it.
