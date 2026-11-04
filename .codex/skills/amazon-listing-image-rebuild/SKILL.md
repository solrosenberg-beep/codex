---
name: amazon-listing-image-rebuild
description: End-to-end rebuild of an Amazon listing's image stack for a Sound Around / Pyle USA brand. Pulls the listing (title, bullets, specs, every image in order) straight from Amazon with a bundled script, no browser needed, reads the matching brand kit from this repo, writes one brief per slot, then generates each replacement image separately (one image per generation call) and saves it. Use this skill whenever the user gives an ASIN or Amazon URL and wants new images made, the stack redone, a hero regenerated, listing images rebuilt, "make me new images for this ASIN", "redo the images", "generate the stack", or wants the audit findings turned into finished image files. For a review-only grade with no image generation, use amazon-listing-image-audit instead.
---

# Amazon Listing Image Rebuild

Takes one ASIN from "current images" to "new image files on disk, one per slot, on brand." Runs in four phases. Do not skip a phase and do not generate any image before Phase 3 is done, because an image generated without the specs and the brand kit will have the wrong numbers and the wrong colors and will be thrown away.

## Phase 1. Open the listing and collect everything

1. Run `python scripts/fetch_listing.py <ASIN>` from this skill's folder. It pulls the title, brand, bullets, spec table, variations, and every listing image in order from amazon.com (or Keepa if `KEEPA_API_KEY` is set) into `work/<ASIN>/listing.md` and `work/<ASIN>/current/01.jpg, 02.jpg, ...`. It needs no packages; it uses only the standard library. Do not look for a "browser tool" and do not ask the user for screenshots first. If the script fails, it prints why. The usual cause is that the environment has no internet; tell the user in one line to turn on Agent internet access for the Codex environment (allow amazon.com and m.media-amazon.com) and start a new task. Only if that is impossible, ask the user to attach the images, bullets and spec table.
   If a browser tool does exist, you may also open the page to read Q&A and reviews, but the script output is the source of record for images and specs.
2. Check `work/<ASIN>/listing.md` has, and fill any gaps by fetching the page yourself with the same method the script uses:
   - Title, brand, price, review count and rating
   - Every bullet point, verbatim
   - The full product information / tech spec table (dimensions, weight, capacity, wattage, temperature range, battery, materials, what is in the box)
   - Variation info: colors, sizes, child ASINs
   - The top 5 questions from the Q&A and the 3 most common complaints in 1 to 3 star reviews (these become image messages)
3. The script already saved every current image to `work/<ASIN>/current/01.jpg`, `02.jpg`, ... in the exact order Amazon shows them. This numbering is the spine of the whole job: every new image you make replaces the current image with the same number, and the finished set is delivered in this same order. Open each one and look at it. Note the hero's aspect ratio.
   Also record the Sound Around SKU (the model number, e.g. PKDRM8, SLSWNG100). It is usually in the title, the "Item model number" spec row, or the user gives it. You need it for the upload folder name.
4. Fetch the search results for the main keyword (first three words of the title, or ask the user) from `https://www.amazon.com/s?k=<keyword>` the same way, pull the top 6 result image URLs and titles, and note in `listing.md`: 1-by or 5-by grid, what the top 6 competitors show on their hero, and what none of them show. If the search page is blocked, say so and move on; it is useful, not required.
5. Write `work/<ASIN>/avatar.md`: who buys this (one specific person) and the pain that sent them searching. Check it against the Q&A and the 1 to 3 star reviews you collected. This person is the model in every lifestyle image and the pain is the subject of at least one before/after slot. See `../amazon-listing-image-audit/references/rules-session-2.md` sections 1 to 3.
6. Write the spec facts you will put on images into `work/<ASIN>/facts.md` as a short list. Only facts that appear on the listing or that the user confirms. A number that is not in `facts.md` does not go on an image. This is the guard against the 900 lb vs 700 lb problem.

## Phase 2. Read the brand kit

1. Identify the brand from the listing (Pyle, SereneLife, NutriChef, Hurtle, Squatz, Pyle Pro, Pyle Vintage).
2. Read `brand-kits/<brand>/BRAND.md` from this repo (relative to this skill: `../../../brand-kits/<brand>/BRAND.md`). Note the hex codes, fonts, logo file path, trust stamp path, approved text/background pairs, photography rules, and the locked stack layout.
3. Load the logo file path (for Pyle: `brand-kits/pyle/assets/pyle-logo-red-transparent.png`). You will composite it onto generated images in Phase 4, not ask the image model to draw it. Image models misspell and warp logos.
4. If there is no `BRAND.md` for the brand, stop and tell the user which brand kit is missing. Do not generate off-brand images and do not invent colors.

## Phase 3. Write one brief per slot

Read `references/rules.md` and `references/rules-session-2.md` in the sibling skill `amazon-listing-image-audit` for the full masterclass rules, then write `work/<ASIN>/briefs.md` using the per-slot template in `references/brief_template.md`. Rules that matter most here:

- One message per image. Count messages across the stack; no duplicates.
- The hero carries the ONE value prop (capacity, weight limit, temperature range, modes, colors). If the product ships in a brown box, the box goes behind the product with the value prop and swatches printed on it. If multi-color, swatches on the hero.
- Every number on an image must be in `facts.md`.
- Text must read at phone thumbnail size: on a 2000 px image, headline 120 px or larger, big numbers 160 px or larger, sub text 60 px or larger. If a message needs more than 5 headline words and 12 sub words, it is two images or it is cut.
- Specs translated to buyer language and US units (inches, quarts, pounds, degrees F).
- Dimensions shown in place (under the cabinet, in the trunk), not on a blank background.
- Realistic quantities and settings. Dishwasher parts on the top rack. Hand-wash parts in the sink. No whole chicken in a basket that cannot hold one.
- Us vs them or before/after for any commoditized claim.
- Every scene is different. This is a hard rule. No two images in the set share the same setting, angle, background color, model, or dish. If slot 2 is a kitchen counter from the front, slot 3 is not a kitchen counter from the front. Vary the room, the surface, the camera angle (front, three-quarter, top-down, close-up), the time of day, the people, and the food. Before generating, list the scene of every slot in `briefs.md` in one line each and check that no two lines match. A repetitive stack looks like one ad on a loop and the buyer stops swiping.
- Never put "not included" disclaimers or "accessories sold separately" text on an image unless the user asks for it. If something is not in the box, leave it out of the picture instead of showing it and disclaiming it. Disclaimers read as a warning and plant doubt. The same goes for asterisks, fine print, and "for illustration only."
- Pets: labs, goldens, dalmatians only. People: ordinary, American home settings, never plastic-looking, and the same avatar body type in every lifestyle slot.
- Every count that decides the purchase is on an image as a big number (bags, modes, feet of cable, colors, capacity). Rank them; the biggest goes on the hero.
- Show the biggest realistic thing it fits. Show the outlet and the cord. Anchor adjustable ranges to an adult and a kid. Translate controls into outcomes. Save-money products get the math on the image. Secondary uses go last or get cut.
- Keep the original order. Brief slot 1 replaces current image 1, slot 2 replaces current image 2, and so on, for every image the listing currently has. Do not add, drop, or shuffle slots on your own. If the current stack has 7 images you deliver 7, numbered the same way. The brand kit's "default stack layout" is a guide for what each slot should say when a listing is being built from scratch, not a license to reorder a live listing.
- If you believe the order should change (a strong value prop buried at slot 7), write that under "Recommended reorder" in `README.md` and leave the files in the original order. The user decides, because reordering changes the thumbnail strip that is already indexed and split-tested.

Show the user `briefs.md` before generating. Ask them to confirm any fact flagged as uncertain. If the user is not available, proceed with only the facts that are on the listing and leave the uncertain ones out.

## Amazon image rules (apply to every image, no exceptions)

Follow Amazon's product image requirements. An image that breaks them gets the listing suppressed, which is worse than a weak image.

Main image (slot 1):
- Pure white background, RGB 255, 255, 255. No gradient, no off-white.
- Only the product that is sold. No props, no accessories not in the box, no people, no mannequins.
- Product fills 85% or more of the frame. Nothing cropped off the edges.
- No text, logos, badges, watermarks, borders, or graphics added in editing. Text that is physically printed on the product or on its real packaging is allowed. That is why the brown-box and side-of-product techniques exist.
- Realistic photo or render of the actual product in the actual color sold. Not a drawing.
- Square, 2000 x 2000 preferred, minimum 1000 px on the longest side so zoom works. Same aspect ratio across the set.
- No multiple views of the product combined into one image.
- For apparel-style items: no mannequins, flat or on a model per Amazon category rules.

Other images (slots 2 and up):
- Text, graphics, lifestyle, infographics, people, and backgrounds are allowed. This is where every value prop, number, and brand panel lives.
- Still no watermarks, no promotional claims Amazon prohibits (no "best seller", "free shipping", "#1", "sale", prices, discount codes), no competitor names or logos in us-vs-them (say "typical competitor" or "others"), no Amazon logos or badges, no customer review quotes, no claims that are not true or not in `facts.md`.
- No offensive or disgusting content, no mixing uses that Amazon or buyers would reject.
- Same square ratio and resolution as the main image.
- JPEG or PNG, sRGB.

If a brief asks for something that breaks a rule above, fix the brief, not the rule.

## The product is shown exactly as it is

The product in every image must be the real product, as shipped, in the color sold. This is a hard rule and it comes before style.
- Use the current main image (or a user-supplied product photo) as the reference for every generation. Pass it to the image model as the source image when the tool allows. The product's shape, proportions, buttons, dials, ports, handles, color, finish, and logo placement must match it.
- Never exaggerate. No bigger basket, no extra drawer, no longer cord, no extra buttons, no sleeker redesign, no "cleaner" version. If the real product has a visible seam, a plain dial, or a short cord, the image shows a visible seam, a plain dial, and a short cord.
- Never add features that are not on the product. No screen it does not have, no light that does not light, no accessory not in the box.
- Never change the size relative to its surroundings. The product sits at true scale next to the counter, the cabinet, the hand, the plate.
- Never fake a result the product cannot produce (a whole chicken in a small basket, a restaurant plating from a home toaster).
- The setting is the only thing you design. Put the real product, unchanged, into the right room, at the right angle, with the right person and the right food. The scene sells; the product stays honest.
- Dimension callouts use the listing's numbers and the drawn product matches those numbers.

Why: a buyer who gets something different from the picture returns it and leaves a one-star review. Amazon also suppresses images that misrepresent the product. An honest product in a great scene beats a flattering product in any scene.

## The first three images are the key images

Buyers on mobile see the main image in search, then swipe. Most never get past image 3. So slots 1, 2, and 3 decide the sale and get the most work:
- Slot 1 (main): clean Amazon-compliant product shot. The value prop rides on the real packaging or the side of the product if possible. This image gets the click.
- Slot 2: the ONE value prop, biggest number, biggest text, product large. This image confirms the click was right.
- Slot 3: the pain solved or the second strongest reason (before/after, us vs them, or "fits your space"). This image closes the doubt.
Spend time in that order. Generate slot 1 first, then 2, then 3, check each one against the QA gate before moving on, and only then do 4 and up. If time or tries run out, a perfect 1 to 3 with flagged 4 to 8 is a better delivery than eight average images. Slots 4 and up still matter; they are where the remaining questions get answered, but they never get worked before 1 to 3 are right.

## Phase 4. Generate each image separately

Generate one image per call. Never ask for a grid, a contact sheet, or "all eight images." One call, one slot, one file. Reasons: each image needs its own composition and its own checking, a multi-image request produces small unreadable panels, and a failed slot should not cost the other seven.

Always in slot order: 1 (main), then 2, then 3, then 4 and up. Never start with an easy lifestyle shot and come back to the main image later. For each slot, in order:

1. Build the prompt from the brief using the pattern in `references/brief_template.md` (section "Prompt pattern"). Put the brand hex codes and font names in the prompt. Ask for the text to be rendered in the image only when the model is reliable at text; otherwise generate the scene with a clear empty panel where the text goes and add the text in step 3.
2. Generate at 2000 x 2000 (or the largest square the tool allows). Save as `work/<ASIN>/new/<SKU>-<NN>.png` where NN is the two-digit slot number matching the current image it replaces (example: `PKDRM8-02.png`). The number comes first in sort order so the folder lists in listing order. Put the message in `README.md`, not the filename.
3. Composite with a script, not by hand (Pillow is preinstalled by the environment Setup script; if it is missing, skip the composite, flag it, and do not pip install inside the task): paste the brand logo from the brand kit at the position the kit specifies, add or correct the text in the brand fonts and hex colors, add the trust stamp if the brief calls for it. Use Pillow or an equivalent. Keep the script in `work/<ASIN>/compose.py` so a rerun is one command.
4. Check the result before moving on. This is the QA gate. First check the product against the reference photo: same shape, proportions, color, controls, ports, and scale, nothing added, nothing enlarged, nothing smoothed away. If the product differs from the reference, it fails and gets regenerated with the reference image and "match the product exactly" in the prompt. Then compare the new image to every slot already finished: if the scene, angle, background, or model repeats one, it fails and gets regenerated with a different scene. Also fail any image carrying a "not included" or "sold separately" line the user did not ask for. Then: no image reaches a human until it passes. Open the file. Confirm: the message reads at 150 px (downscale a copy to 150 px and look at it), every number matches `facts.md`, the colors are the brand hex codes, the logo is not warped, the avatar matches `avatar.md`, the outlet and scale are believable, nothing looks AI-fake (hands, faces, text artifacts, impossible food). Score each check pass/fail in `work/<ASIN>/qa.md`. If a TypeSafe (Jev) image classifier or similar scoring tool is available in the environment, run it on the image with those same checks and record its score too; it costs almost nothing. If any check fails, regenerate that one slot with the fix in the prompt. Up to 3 tries per slot, then flag it for a human designer and move on.
5. Slot 1 (main) must pass every rule in "Amazon image rules" above. Save as `<SKU>-01.png`. If you also made a post-edited variant with added labels, save it as `<SKU>-01-labeled.png` and tell the user the labeled one is a split-test candidate with suppression risk, not a drop-in. The compliant one is always the one that goes in slot 1 of the upload.

## Deliver

Write `work/<ASIN>/README.md` with: the slot list in order (file, what it replaces, message, source fact), what was flagged for a designer, the exact facts used, the recommended reorder if any, and the split-test recommendation. Then give the user the local folder path and the list of files in order, and show the images inline if the environment can. Show thumbnails inline if the environment can display images.

Do not say the stack is done if any slot is flagged. Say which ones are done and which need a designer.

## What this skill does not do

- It does not upload anywhere. The user downloads the `work/<ASIN>/new/` files and uploads them to Vendor Central.
- It does not reorder the stack. It replaces slot for slot and only recommends a reorder in writing.
- It does not break Amazon's image rules for a better-looking image. Compliance beats creativity, every time.
- It does not alter, improve, enlarge, or add to the product. The product is shown as it ships; only the setting is designed.
- It does not invent product capabilities. If it is not on the listing or confirmed by the user, it is not on an image.
- It does not draw the logo with the image model. The logo is always composited from the brand kit file.
