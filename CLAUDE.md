# ENOCH: Ascent of the Scribe — Project Guide

A complete Pokémon-style browser RPG of the **Book of Enoch (1 Enoch)**, built as a
**single-file** vanilla HTML5 Canvas + JS game with a dark biblical-fantasy tone.
No build step, no framework, no dependencies. Open `index.html` and it runs.

---

## Current goal

**Direction change (2026-06-13): art is on hold; the focus is gameplay / structure.**
The user is evolving ENOCH toward a **Pokémon-Mystery-Dungeon-style loop in its own
sacred-horror idiom** — *not* a PMD clone. The framing question is "how do we make ENOCH
feel like a sacred mystery dungeon: missions from the Ledger, expeditions into cursed
places, companions as witnesses, judgment at the end of each descent?" Mapping: Writs of
Judgment = rescue board; Sheol mouth / Jared's Valley = hub; recover names / free souls /
bind Watchers / hunt Nephilim = missions; angels & redeemed spirits = recruits; Sheol
hollows / Hermon ruins / Dudael pits = dungeon floors; Watcher/Nephilim remnant = boss.
Evolve **step by step** — do not rewrite the engine, replace the battle system, or build
procedural dungeons yet. Roadmap order: (1) ✅ mission/expedition wrapper over Writs; (2)
hand-author **The Last Hunger** as the first Sheol expedition (clues→boss→judgment→Abel
reward); (3) visible dungeon enemies that trigger current battles; (4) active companion/
party slots; (5) grid-combat-lite on the map; (6) procedural dungeon floors; (7) writ
board with multiple repeatable missions; (8) optionally convert campaign segments into
expeditions.

The earlier AAA-pixel-art push (Octopath / Triangle Strategy / Sea of Stars targets) is
**paused** — the user is handling graphics separately. Story, systems, and the full
playable arc remain **done and verified**.

---

## What is complete

### Engine & rendering
- **Single file**: `index.html` (~170 KB). Vanilla JS, Canvas 2D, no build.
- **Canvas**: logical `CW=960 × CH=624`; device canvas `1920×1248` via
  `ctx.setTransform(2,0,0,2,0,0)` each frame; `ctx.imageSmoothingEnabled=false`.
- **Tiles**: `TS=48` world tiles. Legacy tile art authored in 32px space
  (`AT=32`, `TSC=TS/AT`) and drawn through a translate+scale wrapper; inside art
  functions `const TS=AT` shadows the global so old 32px code still composes.
- **Masonry**: running-bond blocks, two-step bevels, split courses, protruding
  blocks, carved relief, cracks, moss, glyphs. Palettes `MAS_HERMON`, `MAS_SHEOL`,
  `MAS_DUDAEL`.
- **Density**: `tileDetail()` micro-detail (tufts, rubble, moss creep, floor cracks,
  altar motes); `ditherEdges()` ground-family transitions; wall-cast shadows
  (solid tiles shade floors south/east).
- **Lighting**: global top-left key light + vignette in `lightingPass`, clipped to
  the map rect.
- **Props**: `PROPS` array, `drawProp`, y-sorted tall props, `propSolidAt` collision.
- **Particles**: layers `'world'` (camera-space, map-tagged), `'screen'` (clipped to
  map rect), `'battle'`.

### Sprites
- **Templates**: string-grid sprite templates. `TPL` (32×40 cast) and `TPL_HERO`
  (32×48 Enoch, with `W`/`H` fields). Letter legend: `k` outline, `H/h` hair,
  `S/s` skin, `E` eye, `R/r/Q` robe, `B` belt, `G` gold, `C` collar, `W` staff,
  `M/m` satchel. `tplFor(palKey)` picks the set; rows normalized via
  `padEnd(32).slice(0,32)`.
- **Sprite cache**: `SPRITE_CACHE` pre-renders offscreen canvases at `CSC=3`
  (hero 96×144, cast 96×120) with overlays baked (elder staff, sentinel spear) plus
  a rim-light pass. `getSprite(palKey,facing,frame)`.
- **Walk cycle**: time-based ~6fps (`Math.floor(perf()/160)%4`). Sequence
  `[1,3,2,3]` for Enoch and registered-art chars, `[1,0,2,0]` otherwise. Idle
  breathing (1px settle), stride sway (±1px).
- **Palettes**: `PALS` keyed by character; includes `ohya` (added for QA-004).

### Hybrid asset pipeline (the art track)
- `ASSETS.register(key,src)` / `ASSETS.put(key,img)` / `ASSETS.get(key)`.
- Keys: `char:<pal>:<facing>:<frame>` (facings down/up/side, explicit left
  supported; frames 0 idle, 1 stride-L, 2 stride-R, 3 pass) and
  `tile:<char>[:<map>]`.
- `drawChar` resolution order: **explicit facing → canonical+flip → procedural
  cache**. Procedural art is always the live fallback.
- `ASSETS.exportChar()` provides an artist round-trip (baseline → overpaint).
- **Grok's 65-PNG drop is wired**: 60 character PNGs registered at boot and
  rendering (pipeline proven end-to-end). 5 tile skins registered behind
  `USE_TILE_SKINS=false` (disabled — they regress vs procedural; see gotchas).

### Audio & music
- **SFX**: `tone()` + `sfx{}` tiny synth (blip/confirm/hit/holy/dark/heal/fanfare/step) —
  still in-engine WebAudio.
- **Music — instrumental MP3 tracks (2026-06-15, Hermes agent)**: the earlier procedural
  WebAudio pad/melody/percussion scheduler was **removed** and replaced with looping
  instrumental **MP3s**, one per area/mood at `assets/music/<key>.mp3` (title, earth,
  earth_corrupt, hermon, sheol, heaven, throne, dudael, battle, boss). `MUSIC_TRACKS` +
  `getMusicEl(key)` lazily create one `new Audio('assets/music/'+key+'.mp3')` per key
  (looped, volume 0); `updateMusic(dt)` (called each frame in `loop()`) cross-fades volume
  by view and `currentMusicKey()` picks the track (boss via `B.def.boss`; deeper Sheol maps
  → `sheol`). Source WAV masters live in `assets/music/_wav/` (committed but **not loaded at
  runtime**). ~36 MB of audio total.
- **Controls**: `#musicBtn` mute toggle + `#musicVol` volume slider, persisted to localStorage
  (`enochMusicMuted`, `enochMusicVol`). `primeAudio()` unlocks playback on first keydown/click
  (browser autoplay policy).
- *Constraint note:* this **relaxes the old single-file / procedural-audio rule** (user
  decision 2026-06-15) — music is now external asset files, like the character/tile PNGs.
  `index.html` itself is still a single no-build file.

### Game systems & content
- Full story arc playable and verified: Watchers' fall → intercession branch →
  Sheol → Heavens → Metatron transformation → Flood epilogue.
- State: `F` story flags, `S` stats (right/forbidden/courage/favor/corr), `P` player.
- Save/load: localStorage `'enochSave'`. **Cutscene atomicity**: completion flags
  set at scene end; `if(!cutscene)saveGame()`; `gainArt` dedups.
- **Scribe's Ledger / quest journal (2026-06-13)**: `currentObjective()` and
  `completedMilestones()` **derive** the current quest + milestone list purely from
  `F` flags — *nothing extra is saved* (old-save safe). `currentObjective()` checks
  flags **furthest-progress-first** (reverse order) so any flag combo resolves to the
  correct next step and self-corrects on out-of-order optional beats. The `📜 Scribe (C)`
  panel (`toggleStats`) now leads with an objective box + milestones above the existing
  stats/artifacts/provisions; HUD chip `#chipQ` shows the short objective. Gate-objective
  titles name the gate being approached (Luminaries→Hollow Places→Tree of Life→House of
  Fire). Verified + adversarial review (fixed a gate-title mismatch).
- **Forward-progression gating (2026-06-13)**: map transitions are gated on the prior
  objective's flag so the player can't skip a required beat (a multi-agent sequencing
  audit found these gaps). Gates (each `|| <already-past flag>` for save-compat):
  earth→hermon `cond:F.questHermon||F.fallen` (must hear the boy); earth→sheol
  `cond:(F.petitionDone&&F.soulsHeard)||F.sheolSeen` (Semjaza **and** the altar first);
  heaven→throne `cond:(F.gate1&&F.gate2&&F.gate3)||F.throneSeen` (all three gates).
  Sentinels are now strictly sequential (`sent2 vis F.gate1&&!F.gate2`, `sent3
  F.gate2&&!F.gate3`). Blocked forward tiles show a nudge trigger pointing back to the
  unmet objective. **Return/backtrack warps stay open** — only forward skips are gated.
- **Postgame: The Ledger of Judgment — framework only (2026-06-13, Sprint 1)**: a
  post-story Metatron mode scaffold. State lives under `F` (`F.writs/companions/judgments/
  names`), seeded by `ensurePostgameState()` (called in loadGame/btnNew/toggleStats/
  writState — old-save safe). `WRITS` table (one prototype: `lastHunger`) + helpers
  `writState/unlockWrit/trackWrit/addWritClue/hasWritClue/completeWrit`. `COMPANIONS`
  table is **declarative only** (not wired to combat; existing Uriel `P.party` ally path
  untouched). `currentObjective()` has a top postgame branch (gated on `F.postgame`, set
  ONLY in `endGame`). The Scribe's Ledger shows a "Writs of Judgment" section when
  `F.postgame||F.azazelBound`. `endGame` now **keeps the save** (was `removeItem`), sets
  `F.postgame`, opens `lastHunger`, and adds **CONTINUE AS METATRON** (→ `continueAsMetatron()`,
  drops Metatron at Sheol `2,7`) beside the unchanged **BEGIN A NEW TESTAMENT** (still wipes).
  Verified + 26-agent review (zero defects; campaign unaffected). **No hunt content yet** —
  Sprint 2 ("The Last Hunger": clues→boss→judgment→Abel reward) is next.
  *Map note:* heaven/throne/dudael are cutscene-only islands (no walkable warp to the
  earth/sheol/hermon cluster) — postgame hubs/hunts must live in the walkable cluster or
  use a future writ-board fast-travel.
- **Expedition / mission wrapper (2026-06-13, Sprint 2 groundwork)**: the first step of a
  deliberate **pivot toward a Pokémon-Mystery-Dungeon-style loop** in ENOCH's sacred-horror
  idiom (Writs = rescue board, Sheol mouth = hub, descents = dungeons, companions/redeemed
  spirits = recruits, Watcher/Nephilim = bosses). A Writ can now be **begun like an
  expedition**. New state `F.activeWrit` (the one writ in progress, or `null`) is seeded by
  `ensurePostgameState()` via an **`if(!('activeWrit' in F))` check** (never clobbers a set
  value; old-save safe). `WRITS.lastHunger` gained expedition metadata: `entryMap/X/Y/Face`,
  `returnMap/X/Y/Face` (both Sheol `2,7` for now — see Map note above), `objectiveType:'hunt'`,
  `requiredClues:3`, `boss:'lastHunger'`. Helpers near the writ helpers: `isWritMissionActive(id)`,
  `startWritMission(id)` (refuses non-`locked/open/tracked` writs → completed writs aren't
  re-enterable; chains locked→open→tracked, warps the player à la `continueAsMetatron`,
  `saveGame`s, returns bool), `endWritMission(id,outcome)` (optional `completeWrit`, clears
  `activeWrit`, warps to return point). `currentObjective()`'s postgame branch is now
  three-tier: **active writ** ("Investigate … in <region>") → **idle open/tracked** ("begin a
  Writ …") → **generic** ("Open the Ledger"). The Scribe's Ledger Writs rows now show an
  **Active** marker / Charge / Clues `x/N` / Expedition status, plus a **Begin Expedition**
  button (`window.beginWritFromLedger`, rendered only for open/tracked + `entryMap` +
  `view==='world'`; the inline `onclick` id is quote-escaped). Verified in-browser (old-save
  safety, campaign isolation, start/end/re-entry, save→load persistence of `F.activeWrit`,
  zero console errors) + adversarial multi-agent review (2 latent-hardening findings applied).
- **The Last Hunger — first complete expedition (2026-06-13, Sprint 2)**: the proof-of-loop
  hunt content on top of the wrapper — **Begin Expedition → 3 clues → confront → boss →
  4-way judgment → reward → completed Ledger entry**. All gated on `lastHungerActive()`
  (`F.postgame && isWritMissionActive('lastHunger')`), so the campaign Sheol is untouched.
  Helpers: `lastHungerActive/lastHungerClueCount/lastHungerReady` + `discoverLastHungerClue(id,
  text,sayName)` (records a clue **once**, dedups, flips the writ to `'confronted'` at
  `requiredClues`; does not complete it). **Clues**: `INSPECTS` at Sheol **(6,11)**
  `nameGnawedGrave` + **(19,10)** `hollowBiteMarks` (anchored on the two free *solid* props so
  they're reliably faceable) and **`abelTestimony`** via the **`soul1`** NPC (postgame branch
  at the top of `talk`; campaign dialogue otherwise). Each new inspect has an ambient
  non-active branch so the campaign sees flavor, not clues. **Confrontation**: `INSPECTS`
  **(17,7)** (the deep east, Ohya's old spot) — ambient when idle, "needs more testimony" under
  3 clues, else `note`+`say` → `startBattle('lastHunger')` → on `'win'` → `cs_lastHungerJudgment()`.
  The `ohya` NPC vis gained `&&!lastHungerActive()` so the deep is clear during the expedition
  (provably no campaign effect; in real postgame Ohya is already dead). **Boss**
  `ENEMIES.lastHunger` (hp 140, `xp:0` — reward is the judgment, `boss:true` → boss music,
  `art:'spawn'`; dread carried by the status-only `Empty Grave`, corrupt/drain on damage moves
  per engine rules). **Judgment** `cs_lastHungerJudgment()` — Bind/Destroy/Redeem/Seal, each
  grants **Name of the Deep** (`F.names.deep`) + stat shifts; **Redeem** also sets
  `F.companions.abel` (a *roster* companion — deliberately **not** added to the combat
  `P.party`; shown via the Ledger **Witness** row). Guarded with `if(writState('lastHunger')
  .outcome)return` (additive reward can't double-apply) and completed via `endWritMission`
  (clears `F.activeWrit`, returns to the Sheol mouth, atomic save). `currentObjective()` is now
  clue-aware (**Find clues x/3 → Confront → First Writ sealed**); the Ledger shows Expedition
  status / Outcome / Name gained / Witness and no Begin button once complete. A **boss loss/
  mercy does NOT complete the writ** (retryable). Verified in-browser end-to-end (clue dedup,
  all 4 outcomes, real combat to `win`, mercy-no-complete, save/load round-trip of clues+
  outcome+`names.deep`+`companions.abel`, campaign isolation; zero console errors) + 26-agent
  adversarial review (2 confirmed findings applied: Abel→roster not party, double-apply guard).
- **The Last Hunger — UX polish + hardening (2026-06-14, Sprint 2.5)**: discoverability +
  resilience pass on the expedition (no new systems). **Start guidance**: `beginWritFromLedger`
  adds lastHunger-specific notes naming the three testimonies + the deep-east destination
  (clue-count-aware, so it reads right on Resume). **Ledger testimony checklist**: `□/✔` per
  clue (`hasWritClue`) with location hints, shown only pre-completion; sharper active hint.
  **Resume hardening**: `startWritMission`'s guard now allows **`'confronted'`**
  (`if(!['locked','open','tracked','confronted'].includes(w.status))return false`) so an
  all-clues-but-unjudged writ is resumable; completed outcomes still rejected. The Ledger shows
  a **Resume Expedition** button for a `confronted` writ that isn't active (status in
  open/tracked/confronted). **Easier confrontation**: extracted **`cs_lastHungerConfrontation()`**
  (shared by the (17,7) inspect and a new **step-`TRIGGERS`** entry
  `cond:(x,y)=>x===17&&y===7&&lastHungerReady()&&!writState('lastHunger').outcome`) — walking
  into the deep east with all testimony now starts the fight; the not-ready warning is preserved
  via the inspect. The step-trigger can't double-fire (runScript's `scriptRunning` guard) and is
  inert when not-ready/inactive/completed and during the campaign. Verified in-browser (checklist
  ✔/□ per clue, Begin vs Resume guidance, resume flow, trigger fires only when ready, campaign
  untouched; zero console errors) + adversarial review (**0 findings**).
- **The Last Hunger — deeper Sheol descent (2026-06-14, Sprint 3A)**: turned the one-screen hunt
  into a handcrafted descent — **Sheol mouth → Lower Records → Gnawed Hollow → Hunger Pit**. Three
  new 18×11 maps `sheolRecords/sheolGnawed/sheolHunger` (in `MAPS`; `#` walls + `D/O/E` floors;
  corridor row y=5 open at the doorway edges the WARPS use — Records/Gnawed open both edges, the
  Hunger Pit's east edge stays walled as the deepest). Added `MAPNAMES`/`ARENAS('abyss')`/
  `LOC_SUBS`. **Warps**: descent chain with forward warps `cond:()=>lastHungerActive()` and back
  warps **always open** (never strandable); the deeper maps are intentionally NOT in the warp
  checkpoint list (mercy returns to the Sheol mouth). **Clues relocated**: Abel = original Sheol
  `soul1`; `nameGnawedGrave` = `sheolRecords` (9,4); `hollowBiteMarks` = `sheolGnawed` (9,4) — both
  on solid `stalag` props, recorded via `discoverLastHungerClue`. The old sheol (6,11)/(19,10)/(17,7)
  clue+confront inspects were removed. **Confrontation** moved to `sheolHunger`: a solid `wound`
  lair at (16,5) with the confront inspect, plus a step-`TRIGGERS` at (15,5) (`lastHungerReady()`).
  **Ohya marker**: a glowing `wound` prop at sheol (17,7) `vis:()=>F.postgame` marks where Ohya
  stood + hints the descent. **Prop `vis` support** added to `propSolidAt` + both draw loops
  (`if(p.vis&&!p.vis())continue`) and a new `drawProp` `'wound'` case (purple→gold tear).
  **Ohya hitbox fix**: new `npcInteractAt()` (exact tile, plus within-1 for `big` NPCs — only Ohya)
  used by `tryInteract`; `walkable()` still uses single-tile `npcAt` so collision is unchanged.
  **Rendering/audio routing**: the three `CURMAP==='sheol'` style checks, `lightingPass`, `ambient`,
  and `currentMusicKey` were broadened to `startsWith('sheol')` so the deeper maps render + sound
  as Sheol (`CURMAP` stays `=P.map` so `nbT` neighbor lookups stay correct). Guidance/objective/
  checklist updated for the route. Verified in-browser end-to-end (full descent, clue recording in
  the new maps, confront→judgment→return, back-warps, forward-warp gating, Ohya adjacent interaction
  + campaign fight intact, descent inert in campaign; **screenshot** confirms Sheol look + the wound;
  zero console errors) + 9-agent adversarial review (3 findings applied: `lightingPass`/`ambient`
  `startsWith` + a map comment fix). *Note: postgame Metatron has no random encounters (`rollEncounter`
  returns early on `F.metatron`), so the descent maps are encounter-free — visible enemies are Sprint 3B.*
- **Expedition enemies + witness companions (2026-06-15, Sprint 3B + 4, Hermes agent)**:
  *authored by the concurrent Hermes agent, integrated + verified here.* **Sprint 3B —
  visible expedition enemies**: `EXPEDITION_ENEMIES` (declarative; reuse existing `ENEMIES`
  keys) place on-map foes in the descent maps (`sheolRecords/sheolGnawed/sheolHunger`).
  `expEnemyLive` gates them on the **active writ** (`F.postgame && isWritMissionActive` +
  not judged + not yet felled) so the campaign never sees them; `updateWorld` calls
  `expEnemyAt(nx,ny)` → `engageExpEnemy` (walking into one starts the normal `startBattle`);
  a **win** records the id in `writState(writ).defeatedEnemies` (persisted → stays gone), a
  flee/loss leaves it (retryable); none gate completion. Drawn in `drawWorld` (ghost/red).
  Ledger shows a "Hollow cleared x/N foes" row. **Sprint 4 — active witness companion**:
  `F.activeCompanion` (single COMPANIONS id or null; seeded by `ensurePostgameState`,
  old-save safe). A **redeemed Abel** (from the Last Hunger Redeem judgment) can travel with
  Metatron: a postgame-only **follower** (`witnessFollowerActive`, soul palette, reuses the
  `follower` trail) **plus a capped combat assist** — battle menu `abelAlly` ("First Blood
  Cries Out": modest Holy damage + `expose`, longer cooldown than Uriel). Chosen/dismissed
  from a new Ledger **"Witnesses"** section (`setWitnessFromLedger`/`dismissWitnessFromLedger`).
  Deliberately **separate from the campaign Uriel/`P.party`** path; never active in the
  campaign. Also: `propVisible(p)` centralizes the prop-`vis` check across collision + both
  draw loops. Verified in-browser (enemy live-gating/contact/defeat/persistence, witness
  follower + combat assist + Ledger, campaign isolation, zero console errors); committed to
  `main` with the MP3 audio (commit `8971aaa`).
- Battle: `drawBattleScene` (arena parallax, `platform()`, enemy art 1.5×, hit
  flash `B.hitT`, attack lunge `B.lunge`), `drawCharBig` (back-view, feet at y=160).

---

## Verification workflow (important — hidden-tab throttling)

The preview tab runs hidden, so `requestAnimationFrame` is throttled and
`preview_screenshot` times out. Workaround:

- `.claude/launch.json` defines two servers:
  - **enoch** — `python -m http.server 8413` (serves the game).
  - **shotsink** — `.claude/upload_server.py`, a `ThreadingHTTPServer` on **8414**
    that accepts a base64 POST and writes `.claude/shot.jpg`.
- The page renders frames manually via `preview_eval` and POSTs the canvas JPEG to
  the upload server; then copy/Read `.claude/shot.jpg`.
- Proof shots kept in `.claude/`: `maps_v3.jpg`, `battle_chars.jpg`,
  `masonry_closeup.jpg`, `density_pass.jpg`, `hero_v2.jpg`, `grip.jpg`,
  `fix_verify.jpg`, `grok_wired.jpg`, `final_state.jpg`.

Measured perf: ~7 ms / world frame at 1920×1248. Zero console errors.

**Logic verification (dialog/battle-gated flows), used for the postgame sprints:** game
logic is gated behind dialog confirms and the battle menu, so you can't just call a flow
and read the result. To drive it deterministically via `preview_eval`, temporarily reassign
the top-level functions `note`/`say`/`choice`/`startBattle`/`fadeOut`/`fadeIn` to
auto-resolving stubs (they're reassignable bindings and callers close over them), run the
real orchestration (e.g. an `INSPECTS[...].run()` or `NPCS[...].talk()`), then restore in a
`finally`. For a *real* combat smoke test, battle **messages** auto-advance via timers
(`bmsg`→`wait`) but the move menu (`battleMenuPick`) needs a click: call `startBattle(key)`
directly (skips the pre-battle `note`s), poll for `#bMenu` visible, set `B.hp=1`, and
`.click()` a `.moveBtn`. Always `localStorage.removeItem('enochSave')` + reload afterward —
these tests write to the preview origin's save.

---

## Key decisions & why

- **Single file, no build** — the user's hard constraint; keeps it portable and
  trivially shippable. Don't introduce bundlers, modules, or external JS.
- **Procedural art stays the live fallback** — registered PNGs are an *overlay*, not
  a replacement. Anything missing/unloaded silently falls back, so the game never
  breaks if an asset is absent.
- **`USE_TILE_SKINS=false`** — verified 2026-06-11: static 48px tile skins regress
  vs procedural (path reads as planks; they bypass per-tile variation, wall shadows,
  edge blending, and era tint). Files left untouched per user instruction; re-enable
  only when hand-painted **variant sets** land.
- **Grok is an asset artist only** — HARD RULE: Grok delivers PNGs + markdown docs
  and must **never edit `index.html`**. Past concurrent Grok edits injected broken
  code (see memory `grok-concurrent-edits`).
- **No large base64 in `index.html`** — explicit user rule; keep the file lean.
  Assets live as files under `assets/`.
- **TPL_HERO grip bridge** — hero templates connect hand to staff so Enoch reads as
  holding it.

---

## Known issues & gotchas

- **Dialog must sit above the fade (`#dialog` z-index 16 > `#fade` 15)** — fixed
  2026-06-13. Several cutscenes (e.g. `cs_fall`'s time-skip after Hermon) do
  `fadeOut()` → `note()`/`say()` → `fadeIn()` to narrate over a **black** screen. If
  the dialog drops below `#fade`, those boxes render *behind* the black overlay and the
  game looks frozen (black screen + black text box) while it actually waits for confirm.
  Keep dialog above the fade; `#endScreen` (25) / `#pauseMenu` (30) stay above dialog.
- **Concurrent AI edits**: another tool (Grok) has occasionally written into
  `index.html`. On "File has been modified since read" or mystery `ASSETS` keys,
  re-Read and grep for foreign blocks (stale `32,40` dims, duplicate functions,
  unexpected `ASSETS.put/register` sites). Keep good additions, remove engine-fighting
  ones. (Memory: `grok-concurrent-edits`.)
- **PowerShell UTF-8 mojibake**: `Get-Content` misdecodes UTF-8 as cp1252. Always
  read via `[IO.File]::ReadAllText($p,[Text.Encoding]::UTF8)`.
- **`tile:#:sheol` URL bug**: `#` starts a URL fragment → silent 404. Register with
  `%23` (`tile_%23_sheol.png`).
- **`python` not on shell PATH** on this machine (Microsoft Store stub); launch.json
  uses absolute paths. The upload server must be `ThreadingHTTPServer` (single-thread
  blocks on the harness health-check connection).
- **Tile skins regress** — see decision above; keep disabled.

### QA backlog (from `QA_REPORT.md`, all legit, parked)
- **QA-008 — ✅ FIXED 2026-06-12**: dread no longer stacks a flat `+0.25` onto a
  move's own miss rate. New formula (`index.html` battle turn handler):
  `dreadMul = B.dread>0 ? 0.82 : 1; missChance = 1 - (mv.acc??1)*dreadMul`. Dread now
  scales hit chance multiplicatively → ~18–26% miss under dread (was up to 35%);
  no-dread behavior unchanged. Verified in-browser + adversarial review.
- **QA-006 — ✅ FIXED 2026-06-13**: added `encCooldown` (module var, persisted in
  save/load). `rollEncounter()` no-ops while it's >0; `startBattle()` sets it to **14**
  after a flee, **6** after any fight. Earth grass rate trimmed `0.16 → 0.13`. Gives a
  real post-flee getaway window. Verified + adversarial review (caught + fixed a
  save/load persistence miss).
- **QA-007 — ✅ FIXED 2026-06-13**: bosses stay un-fleeable (story gates), but a
  merciful revival now restocks `Manna≥2, Hyssop≥1` (`Math.max`, so it floors without
  reducing a surplus → no faint-farming) — a wipe can no longer strand the player
  itemless against an un-fleeable boss. (Also: XP curve retuned `level*25 → level*20`,
  ~20% faster, to keep pace with the lower encounter rate.)
- **QA-012 — ✅ FIXED 2026-06-13**: authored a `pass` (mid-step, feet-together) legs
  row for the non-hero `TPL` in all three facings and switched the walk sequence to a
  universal `[1,3,2,3]` — NPCs now do a smooth 4-frame walk instead of popping to idle
  mid-stride. Registered frame-3 art still overrides procedurally. Verified + review.
- **QA-003 — ✅ FIXED 2026-06-13**: pre-reveal Azazel now uses a distinct hooded
  "Stranger" — `PALS.stranger` (world sprite) + `PORTRAITS.stranger` (a `hooded`
  `drawPortrait` branch); `portraitFor` maps STRANGER→stranger, AZAZEL→azazel; the
  earth forge NPC is `pal:'stranger'`, Dudael Azazel stays `pal:'azazel'`. The forge
  dialogue is split so the masked portrait reveals exactly on "I am Azazel". Procedural,
  no new assets. Verified + adversarial review.
- **QA-013 — ✅ FIXED 2026-06-13**: stat chips got `title` tooltips (`.chip`
  pointer-events re-enabled), and the Forbidden Knowledge chip now reads as the *dark*
  stat (purple border/glow via a `.forbidden` class), not scripture. Verified + review.
- **QA-009/010**: referenced `showLocBanner`/`primeAudio`. **Note (2026-06-12):**
  `primeAudio` **does exist now** and is wired (first keydown/click primes the
  AudioContext + music) — the old "hallucinated, doesn't exist" note was stale.
  (`showLocBanner` still unverified; `#locBanner` CSS exists.)

---

## Files

- `index.html` — the entire game (~170 KB).
- `assets/` — Grok's delivery (**do not revert**): 65 PNGs
  (`char_<pal>_<facing>_<frame>.png`: enoch 128×192, NPCs 128×160;
  `tile_*.png` 48×48), `DELIVERY.md` (manifest + register lines),
  `enoch_sheet.jpg` (legacy reference, keep), `build_assets.py` (Grok's generator).
- `QA_REPORT.md` — Grok's 13 QA issues (status above).
- `LORE_NOTES.md` — Grok's dialog proposals (awaiting go-ahead to integrate).
- `.claude/launch.json` — enoch (8413) + shotsink (8414) server configs.
- `.claude/upload_server.py` — base64 POST → `.claude/shot.jpg`.
- `.claude/*.jpg` — verification proof shots.

---

## Exact next steps (prioritized)

1. **Music system — ✅ REPLACED WITH MP3 TRACKS (2026-06-15, Hermes agent).** The earlier
   procedural WebAudio score was removed in favor of looping instrumental **MP3s** under
   `assets/music/` (one per area/mood) — see "Audio & music" above. The single-file/
   procedural-audio constraint was relaxed by the user. *Remaining (optional): confirm the
   final mixes/levels per area; trim `assets/music/_wav/` masters if a leaner repo is wanted.*
2. **Balance pass — ✅ DONE.** QA-008 (dread multiplicative, 2026-06-12); QA-006
   (encounter cooldown + persisted, 2026-06-13); QA-007 (mercy item-floor, 2026-06-13);
   XP curve `level*25 → level*20` (2026-06-13). All verified in-browser + adversarial
   review. Remaining balance work is *feel-tuning only* and needs a human playtest (#6).
3. **Real art overpaints** (the visual ceiling): hand-paint over baseline PNGs —
   Enoch's 12 frames first, then Edna/Elder/Uriel/Azazel. **Enemy battle sprites**
   are now the weakest art (still procedural canvas shapes) — add an `enemy:<key>`
   ASSETS hook (idle + hurt frames) and commission Shade/Beast/Ohya/Semjaza/Azazel.
   Tiles need **variant sets** (4+ per tile + edge pieces) before re-enabling skins.
4. **Content integration — ✅ DONE (2026-06-13).** Inspectable lore hotspots
   (`INSPECTS` array + `inspectAt`, hooked into `tryInteract` after NPC/chest, before
   tile-`L`; 9 flag-conditional hotspots across all maps, anchored on props/features —
   verified all reachable via `walkable()`); distinct pre-reveal "Stranger" (QA-003);
   non-combat **intercede trial** (QA-005 — `F.trialOfPetition`: three ways to write the
   petition, "write both truthfully" rewarded most, none blocking). NPC `pass` frames
   (QA-012) done earlier. Verified + adversarial review. *(`LORE_NOTES.md` lines can
   still be folded into more hotspots if desired.)*
5. **Shipping polish — ✅ MOSTLY DONE (2026-06-13).** Pause/settings menu (Esc/P:
   volume, mute, text speed [persisted], controls reminder, resume, return-to-title
   that saves first), favicon + description/theme-color/OG meta, and an itch.io-ready
   zip (`enoch-ascent-of-the-scribe.zip` — `index.html` at root + 65 PNGs, forward-slash
   entries). All verified + adversarial review. *Remaining (optional): touch controls.*
6. **Human playtest** of the full arc — automated drivers verified flow, not feel.
   **This is now the single most valuable remaining step** (all no-asset engineering done).

**Recommended next session (per the 2026-06-13 pivot):** Sprints 1 (wrapper), 2 (The Last
Hunger loop), 2.5 (UX polish), 3A (deeper Sheol descent maps), **3B (visible expedition
enemies)**, and **4 (active witness companion)** are all done — 3B/4 by the Hermes agent
(2026-06-15), plus the **MP3 music switch**. The next PMD-feeling steps (roadmap in *Current
goal*): a **second hand-authored Writ** (prove the loop repeats with new clues/boss/region —
extend `WRITS` + `EXPEDITION_ENEMIES` for a second `writ`), then **expand the witness roster**
(give Michael/Gabriel/etc. distinct combat assists as more souls are redeemed), then later
**grid-combat-lite → procedural floors → a writ board** (multiple repeatable missions /
fast-travel). Loose ends worth a pass: confirm the new MP3 mixes per area + decide whether to
keep `assets/music/_wav/` masters in the repo. **Art track is paused** (user handling graphics).
**Note:** the **Hermes agent** edits `index.html`/`assets` concurrently — treat surprise diffs as
its work (verify, then integrate), same protocol as the Grok-edit memory.

---

## Working rules

- Keep everything in `index.html`; no build step; no large base64.
- Procedural art is the fallback — never remove it when adding assets.
- Grok delivers assets only; treat unexpected `index.html` diffs as possible
  foreign edits and verify.
- Verify visual changes via the upload-server + `shot.jpg` loop, not
  `preview_screenshot`.
- Read text files as UTF-8 in PowerShell.
