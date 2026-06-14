# ENOCH — Lore & Dialog Proposals

Supplemental writing for engine integration. Tone: reverent, dark, biblical-fantasy — the Book of Enoch filtered through a shepherd-scribe who writes what *is*.

---

## Jared's Valley — ambient notes (inspectable props)

**At the lily near Azazel's forge (earth, x19):**
> White as a prayer that hasn't been answered yet. You touch one petal. It does not wilt. Nothing in this valley wilts anymore — it only waits.

**At the old altar (earth, L tile):**
> The smoke still rises straight. Your grandfather Jared built this when men were few and the sky felt watched. The stone is warm. It should not be warm at night.

---

## Edna — additional lines (post-petition)

**If `F.petitionDone` and `F.corruption`:**
> EDNA: Methuselah asked if you would come home with fewer pages in your satchel or more. I told him: *your father comes home with whatever heaven leaves him.* He is too young to understand that is not comfort.

**If `F.metatron`:**
> EDNA: (She searches your face for the man she married.) The light in your eyes is not cruel. That is all I needed to know. Go. Write the ending. Come back as whatever they have made you — but come back.

---

## Sheol — soul encounters

**Generic ghost (repeatable flavor, no flag):**
> A VOICE: I had a name. It was on my mother's lips twice — once at birth, once at the grave the giants would not let us dig. Write faster, scribe. The ink is the only roof we have.

**Near Ohya's lair (sheol, east tunnels):**
> (The air tastes of copper and old bread.) Something enormous breathes in the dark ahead. Each exhale is a century long.

---

## Heaven — sentinel wrong-answer variants

Alternate rebukes if the player fails a gate quiz twice in one session (engine could track `gateFails`):

**First Gate (luminaries):**
> SENTINEL: Uriel keeps the courses. You keep a satchel. Until you have kept both, you climb in circles.

**Second Gate (hollow places):**
> SENTINEL: You walked among the righteous dead and still answered as one who had not. The spring of light is not a metaphor, scribe.

**Third Gate (Tree of Life):**
> SENTINEL: The Tree's fragrance is already in your bones — you smelled it when you first dreamed of wings. Remember your own lungs.

---

## Throne approach — pre-transform whisper

**Trigger: heaven map, `F.gate3` and not `F.metatron`, stepping on rune tile:**
> <i>A voice without source:</i> The scribe who walks with God is not permitted to remain only a scribe. You will be read aloud.

---

## Dudael — Azazel bound (post-final battle)

**If `F.azazelBound`:**
> (Wind only. The forge is cold. On the sand: a golden mask, cracked, filling with grit the way an hourglass fills with its own glass.) Nothing remains to teach. The lesson outlived the teacher.

---

## Artifact flavor — unused epithets

| Artifact | Epithet line (for stats panel or pickup) |
|---|---|
| Oath Stone of Hermon | *The mountain remembers the oath even when heaven pretends it was never sworn.* |
| Tablet of Judgment | *Semjaza's rebuke, graven. Stone does not argue back.* |
| Key of Sheol | *It opens nothing. It closes everything. You are not sure which frightens you more.* |
| Crown of the Scribe | *Seventy names. One of them is almost His. You have stopped counting how close.* |

---

## Ending epithets (for `endScreen` variants by stat dominance)

| Dominant stat | Epithet |
|---|---|
| Righteousness ≥ 8 | *The Scribe Who Would Not Compromise the Record* |
| Forbidden ≥ 6 | *The Scribe Who Read the Margin and Believed It* |
| Corruption ≥ 5 | *The Scribe Whose Ink Outlasted His Soul* |
| Angelic Favor ≥ 6 | *The Scribe Heaven Carried the Last Mile* |
| Courage ≥ 6 | *The Scribe Who Climbed Because the Dead Could Not* |

---

*All lines are original proposals grounded in 1 Enoch motifs (Watchers' oath, souls of slain, seven heavens, Azazel's binding, Enoch's transformation). Ready for `say()` / `note()` insertion by engine owner.*