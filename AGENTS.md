# Instructions for Codex in this repo

This repo holds Amazon listing image skills and brand kits for Sound Around / Pyle USA. Skills live in `.codex/skills/`, brand kits in `brand-kits/`.

## Getting the listing

Use `.codex/skills/amazon-listing-image-rebuild/scripts/fetch_listing.py <ASIN>`. It reads amazon.com directly (standard library only) and saves title, bullets, specs and every image in order under `work/<ASIN>/`. Do not say "I don't have a browser tool." Do not ask the user for screenshots unless the script reports it has no internet.

## Do not install packages during a task

The task sandbox has no internet for pip. `pip install`, venv creation, npm, apt will hang on retries. Dependencies come from the environment Setup script (`pip install -r requirements.txt`). If Pillow is missing at run time, skip the logo composite, flag it, and keep going. Never create venvs.

## Work folder

All per-ASIN output goes under `work/<ASIN>/`. It is gitignored. Do not commit generated images.

## Which skill

- "audit", "review", "grade the images": `.codex/skills/amazon-listing-image-audit/SKILL.md`
- "rebuild", "make new images", "redo the stack": `.codex/skills/amazon-listing-image-rebuild/SKILL.md`

Both read `brand-kits/<brand>/BRAND.md`. Never invent brand colors or fonts.
