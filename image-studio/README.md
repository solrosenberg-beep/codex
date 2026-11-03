# Image Studio

A plain chat page, like Codex, for rebuilding Amazon listing images. You type an ASIN and what you want, for example:

> B0HJ3R1ZQD rebuild this it has an Auto incline so main image needs to be amazing

It then works through these steps:

1. Reads the Amazon listing: images in order, title, bullets and specs.
2. Reads the image rules and the brand kit from this repo, always the latest on GitHub.
3. Writes a brief for each image (Claude).
4. Generates each new image in the same order (OpenAI), and pastes the real brand logo onto it.
5. Shows original next to new, with **Approve**, **Request Changes** and **Regenerate**. You can also just type changes, like "make the hero text bigger".
6. When you say **save to drive**, it uploads the approved images to the Sound Around image drive as `<SKU>-CODEX`. If nothing is approved, it uploads all of them. **Download the image set** gives you a zip.

Add the word **audit** to get the review and fix briefs without making images.

## Rules are central

The app reads these files from `solrosenberg-beep/codex` on GitHub every 5 minutes:
- `.codex/skills/amazon-listing-image-audit/references/rules.md`
- both `SKILL.md` files
- `brief_template.md`
- `brand-kits/<brand>/BRAND.md`

Edit them on GitHub and the next job uses them, with no restart. The header shows which version of the rules is in use. Logos are read from the app's own copy of `brand-kits/*/assets/`, so a new or changed logo file needs a `git pull` and a restart.

## Set up on Replit (one time)

1. In Replit, choose Create App, then Import from GitHub, and pick `solrosenberg-beep/codex`.
2. Add these in **Tools → Secrets**. They stay on the server and never reach the browser.

   | Secret | What it's for |
   |---|---|
   | `ANTHROPIC_API_KEY` | Reading the listing and writing the briefs (Claude) |
   | `OPENAI_API_KEY` | Generating the images |
   | `GDRIVE_SERVICE_ACCOUNT_JSON` | Save to Drive. Same setup as in the main codex README. |
   | `APP_PASSWORD` | Optional. A team password for the page; any username works. |
   | `KEEPA_API_KEY` | Optional. Reads the listing through Keepa when Amazon blocks the page. |

3. Press **Run** and open the webview. A yellow bar at the top lists any missing secret.
4. To share it with the team, use **Deploy** (a Reserved VM keeps jobs running in the background).

Optional settings: `IMAGE_MODEL` (default `gpt-image-2`), `CLAUDE_MODEL` (default `claude-opus-5-5`), `STUDIO_DRY_RUN=1` (test mode with no API calls and placeholder images).

## When something fails

Every failure shows up in the chat in plain words:
- **Amazon blocks the page:** attach the images with **+**, or add `KEEPA_API_KEY`.
- **An image fails:** press **Regenerate** on that image. The others are kept.
- **Drive fails:** the message names the fix. Your images stay available to download.

Each rebuild costs money in API usage: roughly one Claude call plus one image per slot.
