# Listing Image Studio: developer handoff

Internal tool for the team to audit and rebuild Amazon listing images. The clickable design is `prototype/index.html`, which runs one full product through the whole flow with sample data. This document covers what to build behind it.

Source of truth for rules and brand kits: **github.com/solrosenberg-beep/codex**
- `.codex/skills/amazon-listing-image-audit/SKILL.md` and `references/rules.md`: the audit rules, the hero checklist and the brief template
- `.codex/skills/amazon-listing-image-rebuild/SKILL.md`: the rebuild pipeline, the file naming and the Drive upload behavior
- `.codex/skills/amazon-listing-image-rebuild/scripts/upload_to_drive.py`: the existing Drive upload logic
- `brand-kits/<brand>/BRAND.md` plus `assets/`: colors, fonts, logo files and the locked stack layout for Pyle, SereneLife, NutriChef, Hurtle and Squatz

## 0. Interface: a chat box, like ChatGPT/Codex

The whole tool is one chat thread per product, plus a History sidebar.
- **First message:** an ASIN or Amazon link, plus free text. Parse the ASIN, the mode ("audit" means audit; anything else means rebuild) and the user's emphasis (for example "auto incline, main image must be amazing"). The emphasis goes into the hero brief as a priority.
- **Assistant replies** are structured cards, not just text:
  - progress checklist
  - current-image strip with the top problems
  - fact questions with tap-to-answer buttons
  - an image-set viewer: original next to new, thumbnail column in listing order, Approve, Request Changes and Regenerate, Save to Drive
- **Follow-up messages are edit commands**, for example "make the hero badge bigger", "redo slot 4 with a bedroom", "approve all", "save to drive". Route them with a small LLM intent call that returns `{action, slot, note}`.
- The step names below (Start, Review, Results, Finish) are the stages of the job. In the UI they appear as messages in the thread.

## 1. Non-negotiables

1. **All credentials stay on the server.** The browser never sees the GitHub token, the image-model key or the Google service account. The browser only calls our own API.
2. **The rules live in the codex repo, not in this app.** The app reads them at run time. Changing a rule means editing a file in codex. There is no redeploy and no copy-paste.
3. **Every job records the codex commit SHA it used**, so any image set can be traced back to the exact rules that produced it.
4. **No unconfirmed number goes on an image.** This is the `facts.md` guard from the rebuild skill. Generation is blocked until each fact is confirmed or explicitly left out.
5. **Slots are replaced one for one, in listing order.** We never reorder the images. A recommended reorder is shown as a note only.
6. **One image per generation call.** The logo is composited from the brand-kit file and is never drawn by the model.

## 2. Architecture

```
Browser (React/Vite SPA)  ──►  App API (Node/Express)
                                  │
                                  ├── Rules service ──► GitHub (codex repo, server token, cached by SHA)
                                  ├── Listing service ─► Amazon page fetch / Keepa API / user uploads
                                  ├── Audit service ──► LLM (Claude) with rules.md + BRAND.md as context
                                  ├── Image worker ───► Image model API, one call per slot
                                  │                     └─ compositor (sharp): logo, text, trust stamp
                                  ├── Storage ────────► Object storage (originals, versions, finals)
                                  ├── Drive service ──► Google Drive API (service account, shared drive)
                                  └── Postgres ───────► jobs, slots, versions, facts, events
```

- A **job queue** (pg-boss or BullMQ) runs generation, so a slow or failed slot never blocks the others and the user can close the tab.
- **Push progress to the UI** with server-sent events (`GET /api/jobs/:id/events`), or poll every 2 seconds.

## 3. Rules sync (central updates)

- The server pulls `solrosenberg-beep/codex` through the GitHub API with a fine-grained, read-only token (`GITHUB_RULES_TOKEN`).
- Cache the files by commit SHA. Refresh when either of these happens:
  - a GitHub **push webhook** on `main` arrives (`POST /api/rules/webhook`, verified with `GITHUB_WEBHOOK_SECRET`)
  - a **15-minute** refresh timer fires, as a fallback
- Files to load:
  - `rules.md`
  - `report_template.md`
  - `brief_template.md`
  - both `SKILL.md` files
  - every `brand-kits/*/BRAND.md`
  - every `brand-kits/*/assets/*.png`
- Parse each `BRAND.md` into a typed `BrandKit` record: colors, approved pairs, fonts, logo path and default stack layout. **If parsing fails, keep the last good version and send an admin alert.** Never fall back to made-up colors.
- `GET /api/rules` returns the SHA, the sync time and the file list. The "Rules: codex · main" chip in the header shows this data.
- When a new brand folder appears in codex, it shows up in the brand picker automatically.

## 4. The flow, mapped to the API

| Step | UI | API | Notes |
|---|---|---|---|
| 1. Start | SKU, Amazon link, brand, optional uploads | `POST /api/jobs` (multipart) | Validate the SKU and that the link has `/dp/<10-char ASIN>`. Uploads become the slot images in the order given. |
| 2. Choose | Audit Images or Rebuild Images | `PATCH /api/jobs/:id {mode}` | Starts listing collection: images in strip order, title, bullets, spec table, variations, top Q&A, 1 to 3 star complaints. |
| 3. Review | Current images, top problems, hero scorecard, facts to confirm | `GET /api/jobs/:id/review`, `PUT /api/jobs/:id/facts` | The audit runs the LLM with `rules.md` and `BRAND.md`. Facts are extracted from the listing. Spec conflicts (1700 W vs 1500 W) become questions with one-tap answers. "Leave it off" is always an option. |
| 4a. Results (audit) | Report and one brief per slot | `GET /api/jobs/:id/report` | Download as .docx. "Rebuild these images" switches the mode and keeps the answers. |
| 4b. Results (rebuild) | Original and new side by side, per slot | `POST /api/jobs/:id/generate` | One queued task per slot. Each slot shows Approve, Request Changes (reason chips plus an optional note) and Regenerate. |
| | Approve | `POST /api/slots/:id/approve` (toggle) | |
| | Request Changes | `POST /api/slots/:id/changes {reasons[], note}` | Appends the reasons to the brief, then regenerates. |
| | Regenerate | `POST /api/slots/:id/regenerate` | A new version. Old versions are kept. |
| 5. Finish | Download approved, or save to Drive | `GET /api/jobs/:id/download.zip`, `POST /api/jobs/:id/drive` | Only approved images are included. Files are named `<SKU>-NN.png`. |
| History | Every product, who submitted it, status | `GET /api/jobs?status=` | Filters: All, In review, Needs facts, Done, Failed. |

### Image worker, per slot
This follows phase 4 of the rebuild skill:
1. Build the prompt from the slot brief, using the prompt pattern in `brief_template.md`. Include the brand hex codes and the fonts.
2. Generate at 2000 × 2000.
3. Composite with sharp:
   - the logo from the brand kit, placed where the kit says
   - the headline and sub text in the brand font and brand colors, at least 120 px for headlines and 160 px for numbers
   - the trust stamp, if the brief calls for it
4. Run automatic checks:
   - downscale to 150 px to test readability
   - every number on the image appears in the confirmed facts
   - the colors match the palette
5. If a check fails, retry up to 3 times. After the third failure, mark the slot `needs_designer`.
6. Hero only: produce the Amazon-safe file `<SKU>-01.png` (pure white background, text only on the brown box). Also produce `<SKU>-01-labeled.png` as a split-test candidate. The toggle in the UI picks which one ships.

### Google Drive
- Port `upload_to_drive.py` to the server, or call it directly.
- It uses the shared drive `0AJnODehJPHg5Uk9PVA` and a folder named `<SKU>-CODEX`. It reuses the folder if it already exists and uploads in numbered order.
- Auth comes from `GDRIVE_SERVICE_ACCOUNT_JSON`, set as a server secret. The service account needs Content manager access on the shared drive.
- Save the folder URL on the job and show it in History.

## 5. Data model (Postgres)

- `jobs`: id, sku, asin, amazon_url, brand, mode, status, rules_sha, submitted_by (email from SSO), created_at, updated_at, drive_folder_url
- `slots`: id, job_id, n, role, message, brief_json, status (`queued | generating | ready | approved | failed | needs_designer`), current_version
- `slot_versions`: id, slot_id, v, image_key, prompt, change_reasons, note, checks_json, created_at
- `facts`: id, job_id, key, question, source, answer, confirmed_by
- `events`: id, job_id, type, message, created_at. Feeds the progress display and the audit trail.

Job status values, shown as pills in History:
`draft → collecting → needs_facts → generating → in_review → approved → saved_to_drive`
Failures use `failed:<stage>` with a message a person can act on.

## 6. Errors the user must see in plain words

Each message says what happened and what to do next. The prototype shows the copy for the first three.

| Failure | Message | Action offered |
|---|---|---|
| Amazon page will not load or is blocked | "Amazon didn't return the images." | Try again, or Upload images instead |
| One slot fails to generate | "Slot 6 didn't generate. Your other images are fine." | Try again |
| Drive access is missing | "Couldn't save to Google Drive. Ask IT to share the drive with the app's service account." | Try again, or Download instead. Uploaded files are kept. |
| Rules sync fails | "Using rules from <time>." | A yellow header chip appears. Jobs still run. |
| Brand kit is missing | "No brand kit for <brand>." | Generation is blocked. The skill already forbids off-brand images. |

## 7. Auth and access

- Google Workspace SSO, limited to the company domain. The signed-in email becomes "Submitted by".
- Two roles:
  - **member**: run jobs and approve images
  - **admin**: see every job, retry Drive saves, view rules-sync health
- Server secrets: `GITHUB_RULES_TOKEN`, `GITHUB_WEBHOOK_SECRET`, `IMAGE_MODEL_API_KEY`, `ANTHROPIC_API_KEY` (audit and briefs), `GDRIVE_SERVICE_ACCOUNT_JSON`, `KEEPA_API_KEY` (optional), `DATABASE_URL`, `SESSION_SECRET`.

## 8. Build order

1. Rules service and brand-kit parser, including the header chip.
2. Job creation and listing collection, with upload fallback.
3. Audit and facts (Review screen and audit report). Useful on its own.
4. Image worker and compositor, one slot end to end, then all 7.
5. Approve, Request Changes and Regenerate, with version history.
6. Download and Drive.
7. History, SSO and roles.

## 9. Open decisions for the business

- **Image model.** Which provider to use? Recommendation: keep a small adapter so it can be swapped.
- **Listing data source.** Amazon pages block scrapers, so use Keepa (already in use) for the image list and specs, with uploads as the fallback.
- **Hosting.** Deploy it as its own app, for example on Replit. It reads the rules and brand kits from this same codex repo, so updating a `BRAND.md` or `rules.md` here changes what the tool does.
