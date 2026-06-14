# ENOCH: Ascent of the Scribe

A single-file browser RPG inspired by the Book of Enoch: walk with God, carry the petition of the fallen, descend to Sheol, climb the heavens, and become the scribe of the Throne.

## Play locally

Open `index.html` in a browser, or serve the folder with a local static server.

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## GitHub Pages

This project is ready to publish from the repository root because `index.html` lives at the top level.

Recommended GitHub Pages setting after pushing:

```text
Settings → Pages → Build and deployment → Source: Deploy from a branch
Branch: main
Folder: / (root)
```

The live URL will be:

```text
https://<github-username>.github.io/<repo-name>/
```

## Project structure

- `index.html` — the game
- `assets/` — optional drop-in sprites/tiles
- `CLAUDE.md` — development notes for Claude sessions
- `LORE_NOTES.md` — lore/design notes
- `QA_REPORT.md` — QA notes
