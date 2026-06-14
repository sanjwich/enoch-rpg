# ENOCH — QA Report

**Build tested:** Fable engine `index.html` (canonical)  
**Preview URL:** http://localhost:8413/ (HTTP 200 — server alive at time of report)  
**Assets reviewed:** `assets/DELIVERY.md` batch (not yet registered in engine)  
**Method:** Static code review + server reachability + asset dimension validation. Full playthrough not automated (no browser control in this session).

---

## Critical

### QA-001 — Assets not registered; hand-painted frames never load
- **Map:** Global
- **Repro:** Open game → walk as Enoch → observe procedural sprite only
- **Expected:** If `assets/char_enoch_*.png` are registered, hybrid pipeline should prefer them
- **Actual:** No `ASSETS.register(...)` calls at boot in current engine; pipeline is documented but unwired
- **Severity:** Critical for art milestone (not a runtime crash)
- **Owner:** Engine (Fable) — batch-register per `assets/DELIVERY.md`

### QA-002 — `enoch_sheet.jpg` orphaned
- **Map:** Global
- **Repro:** `assets/enoch_sheet.jpg` exists; engine uses per-frame PNG API, not sheet slicer
- **Expected:** Either sheet is sliced at boot or file is removed from delivery to avoid confusion
- **Actual:** Legacy JPEG sheet unused by current `TPL_HERO` + `ASSETS.register` design
- **Severity:** Medium (workflow confusion)

---

## High

### QA-003 — Azazel overworld uses `azazel` palette before boss form
- **Map:** earth (x19,y13), pre-`F.azazelMet`
- **Repro:** New game → corrupt era → speak to Stranger at forge
- **Expected:** Visually distinct "stranger" silhouette vs final boss
- **Actual:** Same `pal:'azazel'` for NPC and Dudael boss; portrait uses mask art but walk sprite is generic robe
- **Note:** `char_azazel_*.png` helps but needs registration + possibly unique stranger palette

### QA-004 — Ohya NPC reuses `azazel` palette key
- **Map:** sheol (x17,y7), `big:true`
- **Repro:** Enter Sheol → approach Ohya before defeat
- **Expected:** Nephilim/giant distinct from Azazel
- **Actual:** `pal:'azazel'` with `big` scale — reads as scaled Azazel, not unique giant art
- **Severity:** High (boss identity)

### QA-005 — Semjaza battle only on rebuke path
- **Map:** hermon
- **Repro:** Petition path (`F.interceded`) → Semjaza never fought
- **Expected:** Both branches feel equally climactic
- **Actual:** Intercede path skips `startBattle('semjaza')` entirely — half the Hermon arc has no boss encounter
- **Severity:** High (balance/pacing)

---

## Medium

### QA-006 — Random encounter rate may frustrate backtracking
- **Map:** earth (corrupt grass `g`), sheol (`D`)
- **Repro:** Post-fall, walk through tall grass repeatedly
- **Actual:** 16% per step on earth grass; no step cooldown or safe zones after flee
- **Severity:** Medium (balance)

### QA-007 — Flee only available vs non-bosses
- **Map:** Battle
- **Repro:** Fight shade → flee works; fight Semjaza → no flee button
- **Expected:** Documented or consistent (bosses gate flee)
- **Actual:** Correct by design but OHYA/semjaza wipes can drain consumables with no escape — consider boss mercy tuning

### QA-008 — Dread miss chance stacks harshly
- **Map:** Battle
- **Repro:** Receive `dread` status → use low-accuracy move
- **Actual:** `missChance = 0.25 + (1 - acc)` — dread + 90% acc move = 35% miss; prayer at 95% = 30%
- **Severity:** Medium (balance)

### QA-009 — Location banner may overlap dialog
- **Map:** Any warp during active script
- **Repro:** Warp trigger → `showLocBanner` fires while `runScript` dialog queued
- **Actual:** `#locBanner` z-index 8 vs dialog z-index 10 — dialog wins, but banner may flash under HUD awkwardly on fast warps

### QA-010 — Music autoplay requires user gesture
- **Map:** Title
- **Repro:** Load page, wait — no audio until click/key
- **Actual:** Browser policy; `primeAudio()` on interaction — expected, but no on-screen hint except ♪ button
- **Severity:** Low/Medium (UX)

---

## Low

### QA-011 — Tile skins delivered but unwired
- **Map:** hermon `R`, sheol `#`, earth `G`/`P`, dudael `d`
- **Repro:** Register `tile_R_hermon.png` etc. → masonry/grass should swap
- **Actual:** `drawTile` checks `ASSETS.get('tile:...')` — works once registered; procedural fallback active now

### QA-012 — NPC `pass` frame (3) equals idle for non-hero cast
- **Map:** Global animation
- **Repro:** Observe NPC walk cycle
- **Actual:** `TPL` has no `pass` rows; frame 3 falls back to `idle` legs — 4-frame cycle looks like idle-stride-stride-idle
- **Severity:** Low (visual polish; hero `TPL_HERO` has true pass pose)

### QA-013 — `chipF` displays `S.forbidden` but label is 📖
- **Map:** HUD
- **Repro:** Gain forbidden knowledge
- **Actual:** Counter tracks forbidden stat; icon suggests "books" — minor clarity issue

---

## Asset validation (Grok delivery)

| Check | Result |
|---|---|
| Enoch frames (12) | ✅ 128×192 RGBA, transparent, 32:48 aspect |
| NPC frames (48) | ✅ 128×160 RGBA, transparent, 32:40 aspect |
| Tile skins (5) | ✅ 48×48 PNG |
| Naming convention | ✅ `char_<pal>_<facing>_<frame>.png`, `tile_<char>_<map>.png` |
| Engine template match | ✅ Parsed from live `TPL_HERO` / `TPL` — pixel-perfect to procedural fallback |
| Hand-paint ready | ⚠️ Baseline export; artist can overpaint via `ASSETS.exportChar()` templates |

---

## Recommended next steps (engine owner)

1. Batch-register all files in `assets/DELIVERY.md` (one `ASSETS.register` per line).
2. Wire boot hook or inline block after `ASSETS` definition.
3. Playtest Hermon both petition branches for pacing parity.
4. Add `semjaza` + `ohya` to next art sprint (still on generic `TPL`).
5. Re-capture `shot.jpg` after registration to confirm hybrid pipeline.

---

*Report only — no engine files modified.*