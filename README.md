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
| amazon-listing-image-rebuild | Pulls the listing straight from Amazon with a bundled script, reads the brand kit, writes a brief per slot, then generates each replacement image separately in the original slot order and composites the logo. Output lands in `work/<ASIN>/new/`. |

## Rulebook

John Aspinall's rules live in `.codex/skills/amazon-listing-image-audit/references/`: `rules.md` (session 1, Oct 27 2026) and `rules-session-2.md` (session 2, Nov 2 2026). Both skills read both files. Add a new file per session; do not rewrite old ones.

## Brand kits

Short, agent-readable brand rules plus logo files. The image audit skill reads these automatically.

| Brand | File | Status |
|---|---|---|
| Pyle | `brand-kits/pyle/BRAND.md` | Done (from May 2025 guidelines) |
| SereneLife | `brand-kits/serenelife/BRAND.md` | Done |
| NutriChef | `brand-kits/nutrichef/BRAND.md` | Done |
| Hurtle | `brand-kits/hurtle/BRAND.md` | Done |
| Squatz | `brand-kits/squatz/BRAND.md` | Done |

## One-time setup of the Codex environment (web Codex)

Open the `codex` project in web Codex, then **Environment** settings:

1. **Agent internet access: On.** Allow at least `amazon.com`, `www.amazon.com`, `m.media-amazon.com`. (Add `api.keepa.com` if you set a `KEEPA_API_KEY` secret.) Without this the skill cannot read the listing and will ask for screenshots.
2. **Setup script** (runs with internet before each task): `pip install -r requirements.txt`
3. Save, then start a **new** task. Old tasks keep the old environment.

Never pip install inside a task; the task sandbox retries forever. `AGENTS.md` tells Codex the same thing.
