# Independent UI/UX Review: Business Muhurtham Engine

**Score: 5/10 in the first review → 7/10 in a fresh re-review after the fixes.**

## Fix log (first review)

| # | Finding | Status |
|---|---|---|
| 1 | Auto-Select Top 5 picked by date | **Fixed.** Always ranks by score. Step 4 ranks and the print summary are also ordered by score. |
| 2 | No validation; reversed dates accepted | **Fixed.** Inline errors (name, dates, end ≥ start) with `aria-invalid`/`aria-describedby` and `role="alert"`. Proceed is blocked, the end-date picker min follows the start date, and the first error is scrolled to and focused with a toast. |
| 3 | Selections carry over between searches | **Kept by design** (owner's earlier request). It is now flagged: "N shortlisted slots were kept from your previous search". |
| 4–5 | Phone overflow, crushed Step 3 cards | **Fixed.** No horizontal scroll at 375px (Steps 1–4, English and Malayalam). Cards stack with chips flowing across, and the select button is full width. |
| 6 | Header and selection bar too tall on phones | **Fixed.** The header is compact and not sticky on phones, and the selection bar is one 44px line. |
| 7 | Stepper does not follow the active step | **Fixed.** The active tab is scrolled into view. |
| 8 | Stale "Fill from Last Browser Session" | **Fixed.** The session is saved on every search and quick-range change. |
| 9 | "Vris" used for two signs | **Fixed.** Unique labels (Vrsh / Vrsc …). |
| 10 | Ambiguous "Omit …" wording | **Fixed.** "Ignore … rule"; Step 2 is renamed "Rule Settings"; Step 4 tags read "Rule ignored in Step 2". |
| 11 | Label, tooltip and count mismatches | **Fixed.** Preset tooltip matches its label; the Vedic heading says 8 rules. |
| 12 | Silent engine and language side effects | **Fixed.** A toast confirms the engine change and recalculation; the language switch keeps scroll position. |
| 13 | Over-claiming audit copy | **Fixed.** Calmer badges, and it says which engine produced the results. |
| 14 | Cramped Sunrise Convention | **Fixed.** It takes a full-width row. |
| 15 | "Change View" stub, no Sort in calendar, empty weeks | **Fixed.** Sort shows its state and works in Calendar view (orders slots per day). The calendar shows only the weeks in the range. |
| A11y | Headings, stepper, checkbox names, dialog, lang, chart text, contrast, footer targets | **Fixed.** h1/h2 and card headings; keyboard step tabs with `aria-current` and names; named checkboxes and calendar slots (role=button, `aria-pressed`); the audit is a real dialog (`aria-modal`, focus in, Tab trapped, focus returned); `<html lang>` follows Malayalam; chart text 9–12px; light-mode amber 5.0:1; footer targets ≥ 24px. |
| Extra | Found while fixing | "Nature of Business" values never matched the karaka code, so every type except Tech used Jupiter. Now mapped (Retail/Hospitality → Venus, Consulting/Finance → Jupiter, Manufacturing → Saturn, Healthcare → Mars). A missing `updateNatureDescription()` threw an error on every change; that is removed. |

## Re-review (fresh Sonnet reviewer, no context): 7/10

**Fixed straight after the re-review:**
- Rank order in Step 4: #1 89% above #2 91%.
- Off-screen validation error.
- Step change leaves the page mid-scroll.
- Primary button white-on-gold contrast (about 1.7:1 → 5.0:1).
- Missing names on step tabs and system checkboxes.
- No pressed state on presets.

**Open, needing a product decision:**
- **Plain-language explanations.** Results are dense jargon. Add a one-line "why this slot" plus glossary tooltips for chips (Tara, Ashtama, KP sub-lord, QMDJ door).
- **Entity-aware text.** QMDJ "Partnership Peace" appears for a Pvt Ltd. Interpretive text could depend on entity type.
- **Demo defaults.** DOB 1992-08-15 and time 09:30 are pre-filled, so a user could run a chart on demo data. They could start empty and required.
- **Phone header.** Collapse the header actions into a menu and use 44px touch targets. Pills are about 27–30px now; WCAG AA needs 24px, which they pass.
- **Global language.** The Malayalam switch only covers the Step 4 dossier.
- **Naming.** "Fast Math", "Top 5" when only 2 are chosen, and the "Engine: SwissEph AGPL" label.

---

# First review (original report)

_Reviewer: independent senior UI/UX engineer agent (Opus 5.5), given only the app URL and no other context. It used a sandbox copy of the build as of 29 Oct 2026. No code was changed._

## 1. Summary
The app is a 4-step wizard that finds auspicious launch times ("muhurthams") for a new business. You enter the promoter's birth details, the business details and a date range, choose which classical rules to relax, get a scored shortlist, and then see a "Top 5 Deep Scrutiny" dossier with charts and a suggested ceremony schedule. It is aimed at Kerala/Indian entrepreneurs and the astrologers who advise them, and the copy uses a lot of domain jargon (Tarabalam, KP sub-lords, QMDJ). The calculation engine is impressive, and the Malayalam dossier, dark mode, Escape-to-close modal and "Fill from Last Browser Session" are real strengths. But the core flow has trust-damaging bugs. **"Auto-Select Top 5" picks the first five slots by date, not the five highest-scoring ones**, unless you have switched to score sort first. An end date earlier than the start date is silently accepted. Selections from an old run carry into a new one. Phone layout is badly broken. **Overall UX score: 5/10.** The data is rich and capable, but the main shortcut gives wrong results, you can't move through the form without problems, and the layout fails on phones.

## 2. What works well
- The 4-step stepper with plain subtitles ("Promoter, Business & Date Range") makes the shape of the task clear.
- Quick-range buttons (+1 Week / +1 Month / +3 Months / Check Single Day) speed up date entry.
- Step 2 presets (Strict Orthodox Kerala, Commercial Pragmatic, etc.) give non-experts a safe starting point.
- Step 3 slot cards show *why* a slot scored as it did (chips like "Rohini Nakshatra (+10)") and warn about partial overlaps ("Overlaps Yamagandam 15:03-15:30 · Clean: 14:15 - 15:03"). That honesty is excellent.
- The Malayalam toggle translates the whole dossier, including the chart's sign names.
- Dark mode is well tuned: no text in Step 4 fell below 4.5:1 in an automated check. The theme control cycles Auto/Light/Dark with descriptive tooltips.
- Keyboard focus rings are visible on buttons. The audit modal closes with Escape.
- Print styles exist (44 @media print rules), and a "Fill from Last Browser Session" restore is offered.

## 3. Issues (prioritised)

| # | Severity | Area | Issue | Evidence | Recommendation |
|---|---|---|---|---|---|
| 1 | Critical | Core logic / trust | "Auto-Select Top 5" picks the first 5 in the current sort order, not the 5 highest scores. | Step 3, 1400px, Chronological sort (the default): it selected the 30%, 32%, 44%, 48% and 53% slots while 95%, 92%, 91%… went unselected. After switching to Score sort, it picked 95/92/91/89/88. | Always rank by score regardless of view or sort. Add a test for this. |
| 2 | High | Validation | No form validation. An empty name passes, and an end date (20 Oct) before the start date (29 Oct) is silently treated as a single day. | Step 1 → Step 2 → Execute, 1400px: got "Generated 1 eligible slot" with no warning. | Add inline errors with `aria-invalid` and block Proceed. Set the end date's `min` to the start date. |
| 3 | High | State | Selections persist across recalculations. | Ran a 1-day range, then a 1-month range: the old 44% Oct 29 slot stayed "✓ Selected" in the new results. | Clear selections on Redo, or show "1 selection kept from previous run". |
| 4 | High | Mobile layout | The page overflows on phones. The header action row is 444px wide in a 375px viewport, so the layout viewport grows to 468px, and content is clipped at both left and right edges. | 375px: `innerWidth` was 468. "Source Code" button off-screen. Step 3/4 text cut off ("ഒഴിവാക…", "Penalt…"). | Wrap or collapse header actions into a menu, and add `min-width:0` and wrapping to flex children. |
| 5 | High | Mobile layout | Step 3 slot cards are crushed into three columns. | 375px: time breaks onto 4 lines ("09:15 - / 10:00 / (Target: / 09:20)"), each chip wraps, and the "+ Select for Scrutiny" button overflows. | Stack the card at <600px (score + time on top, chips below, full-width select button). |
| 6 | Medium | Mobile chrome | Too much screen is taken by fixed UI. The header is about 200px tall, and the sticky "0 of 5 Candidates Selected" bar covers another quarter of the screen. | 375×812, Step 3. | Compact the header on scroll and make the selection bar a slim one-line bar. |
| 7 | Medium | Navigation | On phones the stepper scrolls sideways but doesn't follow the active step. | 375px, on Step 4: only steps 1–2 were visible. | Scroll the active step into view, or show a compact "Step 4 of 4" on mobile. |
| 8 | Medium | Persistence | "Fill from Last Browser Session" restored a stale range (end 2026-10-20), not the last-used +1 Month (2026-11-29). | Reloaded at 375px and clicked the restore button. | Save the session on every calculation, not only the first. |
| 9 | Medium | Content accuracy | The D1 chart uses the abbreviation "Vris" for both Vrishabha (Taurus) and Vrischika (Scorpio). | Step 4, English mode: two "Vris" cells in the same chart. | Use "Vrsh" and "Vrsc", or full names. |
| 10 | Medium | Microcopy | The "Omit …" checkboxes are ambiguous. "Omit Rahu Kalam" could mean "avoid Rahu Kalam" or "ignore the rule". | Step 2. | Reword as "Allow slots during Rahu Kalam" or "Ignore Rahu Kalam rule". |
| 11 | Medium | Consistency | Labels disagree with each other. The preset's visible label is "Commercial Pragmatic" but its accessible name and tooltip say "Office & Banking Hours". The heading says "Vedic & Kerala Panchangam (7 Rules)" above 8 checkboxes and a sunrise setting. | Step 2, 1400px. | Make labels, tooltips and counts match. |
| 12 | Medium | Feedback | Engine and language toggles trigger silent side effects. Clicking "Engine" instantly recalculates (Swiss → Swiss Only → Internal Only), with only a small timestamp line changing. The language toggle jumps the page to the top. | Header and Step 4, 1400px. | Use a labelled menu, show a toast saying results were recalculated, and keep the scroll position. |
| 13 | Low | Trust / tone | The copy overclaims. The audit modal shows simplified formulas labelled "MATHEMATICALLY PROVEN" and "VERIFIED DETERMINISTIC" while also saying Swiss Ephemeris is active. Brand-like phrases ("Fast Math", "Executive Dossier") sit next to jargon. | Internal Logic Audit modal. | Use calmer, verifiable language and explain which engine produced which numbers. |
| 14 | Low | Layout | The "Sunrise Convention" helper text is squeezed into a roughly 80px column, about 10 lines tall. | Step 2, 1024px. | Give it a full-width row. |
| 15 | Low | Visual | A greyed-out "Change View" label sits next to the "View: List" button and looks like a disabled button. The Sort button disappears in Calendar view. The calendar shows 28 empty days before the range starts. | Step 3. | Merge into one toggle, and start the calendar at the range's first week. |

## 4. Accessibility findings
- **No headings anywhere** (zero h1–h6). Step titles are styled divs, so screen-reader users cannot navigate by heading (WCAG 1.3.1, 2.4.6).
- **The stepper tabs are `div`s with tabIndex −1**, so there is no keyboard access to jump between steps and no `aria-current` (2.1.1, 4.1.2).
- **Slot selection checkboxes have no accessible name.** The tree reads them as "checkbox on", repeated 21 times (4.1.2, 1.3.1).
- **The audit modal has no `role="dialog"` or `aria-modal`, and focus stays on the trigger button behind the backdrop** (2.4.3, 4.1.2). Escape does close it, which is good.
- **The `<html lang>` stays "en" after switching to Malayalam**, so screen readers will mispronounce the text (3.1.1/3.1.2).
- **Kundali chart text is 8.5px**, and the Malayalam planet labels in the chart are illegible (1.4.4 practical readability).
- **Amber text (#D97706) on white fails contrast at about 3.1–3.2:1.** This affects "Auspicious Window…" (13.6px) and the ceremony heading (12.8px) in light mode (1.4.3). Dark mode passed.
- **Footer links are 16–17px tall**, below the 24px minimum target (2.5.8).
- **Positives:** form fields have proper `<label>`s, buttons show a visible focus ring, and a `prefers-reduced-motion` rule exists.

## 5. Mobile findings (375×812)
- The page overflows horizontally: the header actions are 444px wide, the layout viewport becomes 468px, and content is clipped on both edges in Steps 2–4.
- The header buttons wrap into 4-line pills ("Engine: / SwissEph / AGPL / (Default)") and take about 200px of height.
- Step 3 cards are unusable. The time wraps over 4 lines, chips stack one per line, and the select button overflows the card.
- The sticky selection bar ("0 of 5 Candidates Selected for Deep Dive") wraps to 5 lines and covers content. Its disabled "Select Candidates Above" button has low contrast.
- The stepper scrolls sideways and doesn't show the current step.
- Step 1's form does stack cleanly to one column, and the date/time inputs are full width, which is good.

## 6. Quick wins
1. Make "Auto-Select Top 5" always rank by score (a one-line sort fix).
2. Add date-range and required-field validation (end ≥ start, name required) with inline messages.
3. Clear or flag stale selections on every recalculation.
4. Let the header actions wrap or collapse (`flex-wrap`, or an overflow menu under 600px) to remove mobile horizontal scroll.
5. Turn step titles into real headings, stepper items into buttons with `aria-current`, and label each slot checkbox (for example "Select Nov 26, 08:59–09:12, 95%").

## 7. Method
- **Viewports and themes:** desktop at 1400×900 (emulated) and the pane's native 1024px; phone at 375×812. Light and dark via `prefers-color-scheme`, plus the in-app theme toggle (Auto → Light → Dark → Auto).
- **Task run end to end:** filled Step 1 with made-up data (Meera Pillai, Pillai Spice Exports, Kerala spice exports). Tested an empty-name submit and a reversed date range, then +1 Month. Applied the Commercial Pragmatic preset, executed, tried Auto-Select under both sorts, Clear, List/Calendar views, and Scrutinize (5). In Step 4 checked the Malayalam toggle and the Internal Logic Audit modal (keyboard Enter and Escape).
- **Also exercised:** the engine toggle (recalculation), reload, and "Fill from Last Browser Session".
- **Checks:** contrast was measured by script with alpha compositing, along with headings, labels and roles.
- **Not tested:** the actual print dialog (only confirmed print CSS exists); external links (Contact Institute, GitHub, footer links were only noted); screen-reader output with a real assistive technology; and whether the astrological calculations are correct.
- **Caveat:** screenshots in the browser pane sometimes lagged or were cropped, so states were confirmed via DOM inspection.
