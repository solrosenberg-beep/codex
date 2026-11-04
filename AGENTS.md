# Instructions for Codex in this repo

This repo holds Amazon listing image skills and brand kits for Sound Around / Pyle USA. Skills live in `.codex/skills/`, brand kits in `brand-kits/`.

## STOP RULE 1: brand kit before any image (non-negotiable)

Every image job (rebuild, new callouts, restyle, single hero) runs `.codex/skills/amazon-listing-image-rebuild/SKILL.md`. Do not freelance with your own search, curl, or prompts.

Before generating or editing ANY image, post this line in chat, filled in from the files:

    Brand: <brand from the listing title/brand field>  Kit: brand-kits/<brand>/BRAND.md  Colors: <every HEX from its Colors table>  Fonts: <headline/body>

If you cannot fill that line, you have not read the kit, so stop and read it. Every panel, headline, number and accent uses only those HEX codes. Red is a Pyle color; it never goes on SereneLife, Hurtle, NutriChef or Squatz. Teal is SereneLife; it never goes on Pyle.

After each image: `python .codex/skills/amazon-listing-image-rebuild/scripts/brand_check.py <brand> <file>`. FAIL means regenerate that slot with the brand HEX codes in the prompt. Never show the user an image that failed. If the user asks to match the "old" or "original" listing style, keep the layout they point to but still use the brand kit colors and fonts, unless they say in words to drop the brand kit.

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
