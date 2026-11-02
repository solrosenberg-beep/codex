# Codex skills

Skills for OpenAI Codex (also work in Claude). One folder per skill under `skills/`.

## Install on a new machine

Windows (PowerShell):

    git clone https://github.com/solrosenberg-beep/codex $env:USERPROFILE\codex-skills
    New-Item -ItemType Directory -Force $env:USERPROFILE\.codex\skills | Out-Null
    Copy-Item -Recurse -Force $env:USERPROFILE\codex-skills\skills\* $env:USERPROFILE\.codex\skills\

Mac / Linux:

    git clone https://github.com/solrosenberg-beep/codex ~/codex-skills
    mkdir -p ~/.codex/skills && cp -r ~/codex-skills/skills/* ~/.codex/skills/

Then run `codex --list-skills` to confirm.

## Skills

| Skill | What it does |
|---|---|
| amazon-listing-image-audit | Grades an Amazon hero image and image stack against the Sound Around image masterclass rules and writes per-image fix briefs (review only, no image generation) |
| amazon-listing-image-rebuild | Opens the listing, collects images and specs, reads the brand kit, writes a brief per slot, then generates each replacement image separately and composites the logo |

## Brand kits

Short, agent-readable brand rules plus logo files. The image audit skill reads these automatically.

| Brand | File | Status |
|---|---|---|
| Pyle | `brand-kits/pyle/BRAND.md` | Done (from May 2025 guidelines) |
| SereneLife | | Needed |
| NutriChef | | Needed |
| Hurtle | | Needed |
