---
name: amazon-listing-image-rebuild
description: End-to-end rebuild of an Amazon listing's image stack for a Sound Around / Pyle USA brand. Opens the listing, collects the current images and specifications, reads the matching brand kit from this repo, writes one brief per slot, then generates each replacement image separately (one image per generation call) and saves it. Use this skill whenever the user gives an ASIN or Amazon URL and wants new images made, the stack redone, a hero regenerated, listing images rebuilt, "make me new images for this ASIN", "redo the images", "generate the stack", or wants the audit findings turned into finished image files. For a review-only grade with no image generation, use amazon-listing-image-audit instead.
---

# Amazon Listing Image Rebuild

Takes one ASIN from "current images" to "new image files on disk, one per slot, on brand." Runs in four phases. Do not skip a phase and do not generate any image before Phase 3 is done, because an image generated without the specs and the brand kit will have the wrong numbers and the wrong colors and will be thrown away.

## Phase 1. Open the listing and collect everything

1. Open `https://www.amazon.com/dp/<ASIN>` with the browser tool. If no browser tool is available, ask the user for: the listing URL, screenshots of every current image, the bullet points, and the tech spec table. Do not guess at any of it.
2. Collect and save to `work/<ASIN>/listing.md`:
   - Title, brand, price, review count and rating
   - Every bullet point, verbatim
   - The full product information / tech spec table (dimensions, weight, capacity, wattage, temperature range, battery, materials, what is in the box)
   - Variation info: colors, sizes, child ASINs
   - The top 5 questions from the Q&A and the 3 most common complaints in 1 to 3 star reviews (these become image messages)
3. Save every current listing image to `work/<ASIN>/current/01.jpg`, `02.jpg`, ... in slot order. Right-click save, or read the image URLs from the page and download them. Note the hero's aspect ratio.
4. Open the search results for the main keyword (take it from the first three words of the title or ask the user). Save a screenshot as `work/<ASIN>/serp.png` and note in `listing.md`: 1-by or 5-by grid, what the top 6 competitors show on their hero, and what none of them show.
5. Write the spec facts you will put on images into `work/<ASIN>/facts.md` as a short list. Only facts that appear on the listing or that the user confirms. A number that is not in `facts.md` does not go on an image. This is the guard against the 900 lb vs 700 lb problem.

## Phase 2. Read the brand kit

1. Identify the brand from the listing (Pyle, SereneLife, NutriChef, Hurtle, Squatz, Pyle Pro, Pyle Vintage).
2. Read `brand-kits/<brand>/BRAND.md` from this repo (relative to this skill: `../../../brand-kits/<brand>/BRAND.md`). Note the hex codes, fonts, logo file path, trust stamp path, approved text/background pairs, photography rules, and the locked stack layout.
3. Load the logo file path (for Pyle: `brand-kits/pyle/assets/pyle-logo-red-transparent.png`). You will composite it onto generated images in Phase 4, not ask the image model to draw it. Image models misspell and warp logos.
4. If there is no `BRAND.md` for the brand, stop and tell the user which brand kit is missing. Do not generate off-brand images and do not invent colors.

## Phase 3. Write one brief per slot

Read `references/rules.md` in the sibling skill `amazon-listing-image-audit` for the full masterclass rules, then write `work/<ASIN>/briefs.md` using the per-slot template in `references/brief_template.md`. Rules that matter most here:

- One message per image. Count messages across the stack; no duplicates.
- The hero carries the ONE value prop (capacity, weight limit, temperature range, modes, colors). If the product ships in a brown box, the box goes behind the product with the value prop and swatches printed on it. If multi-color, swatches on the hero.
- Every number on an image must be in `facts.md`.
- Text must read at phone thumbnail size: on a 2000 px image, headline 120 px or larger, big numbers 160 px or larger, sub text 60 px or larger. If a message needs more than 5 headline words and 12 sub words, it is two images or it is cut.
- Specs translated to buyer language and US units (inches, quarts, pounds, degrees F).
- Dimensions shown in place (under the cabinet, in the trunk), not on a blank background.
- Realistic quantities and settings. Dishwasher parts on the top rack. Hand-wash parts in the sink. No whole chicken in a basket that cannot hold one.
- Us vs them or before/after for any commoditized claim.
- Pets: labs, goldens, dalmatians only. People: ordinary, American home settings, never plastic-looking.
- Follow the brand kit's locked stack order unless the product's category makes a slot pointless; then say why in the brief.

Show the user `briefs.md` before generating. Ask them to confirm any fact flagged as uncertain. If the user is not available, proceed with only the facts that are on the listing and leave the uncertain ones out.

## Phase 4. Generate each image separately

Generate one image per call. Never ask for a grid, a contact sheet, or "all eight images." One call, one slot, one file. Reasons: each image needs its own composition and its own checking, a multi-image request produces small unreadable panels, and a failed slot should not cost the other seven.

For each slot, in order:

1. Build the prompt from the brief using the pattern in `references/brief_template.md` (section "Prompt pattern"). Put the brand hex codes and font names in the prompt. Ask for the text to be rendered in the image only when the model is reliable at text; otherwise generate the scene with a clear empty panel where the text goes and add the text in step 3.
2. Generate at 2000 x 2000 (or the largest square the tool allows). Save as `work/<ASIN>/new/<slot>-<message-slug>.png` (example: `02-dual-basket-8-8qt.png`).
3. Composite with a script, not by hand: paste the brand logo from the brand kit at the position the kit specifies, add or correct the text in the brand fonts and hex colors, add the trust stamp if the brief calls for it. Use Pillow or an equivalent. Keep the script in `work/<ASIN>/compose.py` so a rerun is one command.
4. Check the result before moving on. Open the file. Confirm: the message reads at 150 px (downscale a copy to 150 px and look at it), every number matches `facts.md`, the colors are the brand hex codes, the logo is not warped, nothing looks AI-fake (hands, faces, text artifacts, impossible food). If any check fails, regenerate that one slot with the fix in the prompt. Up to 3 tries per slot, then flag it for a human designer and move on.
5. Hero only: also produce the Amazon-compliant version. Pure white background (RGB 255,255,255), product fills 85% or more of the frame, no logo overlay on the product itself, no text other than what is physically printed on the product or its box. Save as `01-hero.png`. If you also made a post-edited variant with labels, save it as `01-hero-labeled.png` and tell the user the labeled one is a split-test candidate with suppression risk, not a drop-in.

## Deliver

Write `work/<ASIN>/README.md` with: the slot list (file, message, source fact), what was flagged for a designer, the exact facts used, and the split-test recommendation. Then give the user the folder path and the list of files. Show thumbnails inline if the environment can display images.

Do not say the stack is done if any slot is flagged. Say which ones are done and which need a designer.

## What this skill does not do

- It does not upload to Vendor Central or Seller Central. The user uploads.
- It does not invent product capabilities. If it is not on the listing or confirmed by the user, it is not on an image.
- It does not draw the logo with the image model. The logo is always composited from the brand kit file.
