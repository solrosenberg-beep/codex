# Codex skills

Skills for OpenAI Codex (also work in Claude). One folder per skill under `.codex/skills/`, which is where Codex looks for repo-level skills.

## Web Codex (chatgpt.com/codex)

Nothing to install. Connect this repo (`solrosenberg-beep/codex`) as the project in web Codex and the skills in `.codex/skills/` load automatically. Brand kits are read from `brand-kits/`.

## Desktop Codex, Codex app, or CLI on a PC

Windows (PowerShell):

    git clone https://github.com/solrosenberg-beep/codex $env:USERPROFILE\codex-skills
    New-Item -ItemType Directory -Force $env:USERPROFILE\.codex\skills | Out-Null
    Copy-Item -Recurse -Force $env:USERPROFILE\codex-skills\.codex\skills\* $env:USERPROFILE\.codex\skills\

Mac / Linux:

    git clone https://github.com/solrosenberg-beep/codex ~/codex-skills
    mkdir -p ~/.codex/skills && cp -r ~/codex-skills/.codex/skills/* ~/.codex/skills/

No git? Ask Claude for the zip and run:

    Expand-Archive -Force "$env:USERPROFILE\Downloads\codex-skills.zip" "$env:USERPROFILE\.codex\"

Then restart Codex.

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
| SereneLife | `brand-kits/serenelife/BRAND.md` | Done |
| NutriChef | `brand-kits/nutrichef/BRAND.md` | Done |
| Hurtle | `brand-kits/hurtle/BRAND.md` | Done |
