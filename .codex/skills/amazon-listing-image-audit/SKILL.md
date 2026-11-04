---
name: amazon-listing-image-audit
description: Audit and rebuild an Amazon listing's hero (main) image and image stack using the Sound Around image masterclass rules (John Aspinall, Oct 2026). Use this skill whenever the user shares an ASIN, listing URL, product name, or screenshots of listing images and wants them reviewed, graded, critiqued, torn down, fixed, redone, or rolled out across a product line. Trigger on "audit the images", "review this listing", "hero image", "main image", "image stack", "listing images", "why isn't this converting", "CTR on this ASIN", "tear down this ASIN", "what should the images say", "image briefs", "roll out to the other air fryers", or any request to improve Amazon product photos, infographics, or A+ for a Pyle, SereneLife, NutriChef, Hurtle, or Squatz item. Do not use for PPC, pricing, or inventory reports.
---

# Amazon Listing Image Audit

This skill turns the Sound Around image masterclass (John Aspinall, L10 Sales meeting, Oct 27 2026) into a repeatable audit. The whole philosophy fits in one line: **the hero image must sell on its own, every stack image must say one thing, and everything must be readable by a 70-year-old on a phone in sunlight.**

Why this matters: Amazon is split-testing hiding A+ content and the brand story, showing only the hero and the image stack (like Temu or Shein). Click-through rate is the easiest lever in the whole listing because only five things move it (title, price, reviews, coupon, hero image) and the hero is the only one a buyer controls freely. John spends 50% of creative time on the hero, 35% on the stack, 15% on everything else.

## Inputs you will get

One or more of:
- An ASIN or listing URL
- A product name plus brand (Pyle / SereneLife / NutriChef / Hurtle)
- Screenshots of the current hero and stack images
- Sometimes the A+ content screenshots too

If you only have an ASIN and a browser tool is available, open the listing and the search results page for the main keyword. If no browser is available, ask the user for screenshots of the hero, the full stack, and the top 6 search results for the main keyword. Do not guess what the images look like.

## The workflow (always in this order)

### Step 1. Look at the search results page FIRST
Never critique a hero image in a vacuum. Search the main keyword and note:
- Is it a 1-by SERP (one product per row, appliances) or a 5-by SERP (wide grid)? 1-by is harder; 5-by gives more room to stand out but everyone looks the same.
- What are the top 6 competitors showing? (lifestyle, packaging, text callouts, color swatches, people on the product, scale references)
- What is NOBODY showing that we could show? That gap is the decommoditizer.

### Step 2. Name the avatar and the pain
Write two lines before anything else: who buys this (the specific person, not the category) and what pain sent them searching. A 330 lb toilet is bought by a heavy adult afraid it will collapse. A vacuum sealer is bought by a Costco shopper tired of throwing out food. A curb ramp is bought by someone whose bumper scrapes. If the current images speak to a different avatar (grandpa with a walker, a skinny model, a podcaster for a mic with no USB), that is finding number one. Read `references/rules-session-2.md` sections 1 to 3.

### Step 3. Find the ONE value prop
Ask the buyer's question: what is the pain that brought them here, and why this solution instead of the obvious one? (Bucket towel warmer instead of wall mount: renter, no space. Air fryer: broke the old one, or wants to eat healthier. Saucer swing: 900 lb capacity means the whole family can pile on.)

Pick the single strongest differentiator vs the SERP. Usually it is one of: capacity or size, weight limit, temperature or power range, number of modes, number of colors available, or a multi-use claim. That one thing goes on the hero.

### Step 4. Grade the hero image
Score each item pass/fail. Read `references/rules.md` section "Hero image" and `references/rules-session-2.md` for the full detail.

0. Is it Amazon-compliant? Pure white background, product only, 85% fill, no added text or logos or badges (text printed on the real product or packaging is fine), square, 1000 px or larger. A non-compliant main image is finding number one, above everything else, because it gets the listing suppressed.
1. Can the buyer learn the ONE value prop from this image alone? (Treat it as the only image they will ever see.)
2. If the parent has multiple colors, is a color swatch or color strip visible? (Buyer who dislikes the shown color scrolls past without ever knowing a second color exists.)
3. Is any text callout large enough to read on a phone thumbnail? (If you cannot read it, delete it. "9 modes" in a tiny label is wasted.)
4. If the item ships in a brown box, is the brown box behind the product carrying the value prop and swatches? (Do not fake retail packaging; just enhance the brown box. Packaging behind the product is the lowest-suppression-risk way to add text.)
5. Does the image show the real product, unchanged? Same shape, proportions, color, controls, ports, cord, and scale as the real item; flag any exaggeration, added feature, redesign, or size inflation. And does it match the real spec? (The swing said 900 lb in the hero and 700 lb deeper in the stack. That kills conversion after the click.)
6. Does the thumbnail aspect ratio match the full image? (A slim thumbnail that opens to a wide image creates doubt.)
7. Is the parentage clean? Flag any child that is actually a different product, or two identical children with different names (black vs "black legacy") that only differ in cost test. Amazon's bot is breaking these up anyway. Also flag two listings of the same product whose images show different shapes; one set is wrong.
8. Are the counts on the hero? Bags, wipes, cable feet, modes, colors, capacity. Rank them by what decides the purchase and check the biggest is on the hero (session 2, rule 4).
9. Does the hero show the biggest realistic thing it fits (bagel, not toast)?

### Step 5. Grade the image stack, one image at a time
Images 1, 2, and 3 are the key images: most mobile buyers never swipe past 3. Grade those three hardest and put their fixes at the top of the Top 3 list. Also check every stack image for Amazon rule breaks: no prohibited claims (best seller, free shipping, sale, prices), no competitor names or logos, no Amazon badges, no review quotes, no watermarks.

For every image in the stack ask: **what does this image SAY?** If the answer is "nothing" or "the same thing as image 3", it is a wasted slot. Read `references/rules.md` section "Image stack" for the checklist. The hard rules:

- Every image has one purpose, stated in large text. No duplicate messages (two "dual cook" images is one wasted slot).
- The avatar is the model. Same body type and life situation in every lifestyle shot, matched to the buyer (big guy for a 330 lb capacity product).
- The pain is shown. Before/after or problem/solution appears at least once when the pain is visual (bumper on curb, brown lettuce, burnt toast).
- Realism checks from session 2: outlet and cord shown, scale believable (under a cabinet, not mid-island), shipped bag matches the photo bag, collapsed vs expanded labeled with arrows, no disgust mixing, no sealing grapes or chips, adjustable ranges anchored to an adult and a kid.
- Controls translated to outcomes ("pick the toast color" beats "levels 1 to 6"), and the competitor's confusing version shown next to ours.
- Secondary uses (stool, wine, walker) are last or cut. Uses the product cannot do (podcast with no USB) are gone.
- Mobile first. Text and the product itself fill the frame. Small diagrams of how-to-use steps are the most common failure; they should be top-to-bottom full-size.
- Realistic use. Food is not crammed to the brim. A whole chicken is not in an air fryer that cannot hold one. Nobody props two air fryers on a marble counter. A dishwasher-safe part is shown on the top rack; a hand-wash part is shown in the sink.
- Dimensions must answer "why do I care": will it fit under my cabinet, in my kitchen, in my car. Show it in that spot.
- Translate specs into buyer language. "58 mm ETPU ball" means nothing in the US. "Tennis-ball size, soft, safe for teeth" does. "USB-C" means "uses the charger you already own". "Rechargeable" means "3 to 4 hours of park play, no cord".
- Us vs them and before/after are the strongest formats for commoditized claims (non-stick, temperature control, weight capacity).
- The product is shown as it is. Flag any image where the product looks bigger, sleeker, or more featured than the real one, or sits at the wrong scale in the scene. The setting can be designed; the product cannot be changed.
- Every scene is different. Flag any two images that share the same setting, angle, background, model, or dish. A repetitive stack is a top-3 finding.
- Flag any "not included" or "sold separately" disclaimer, asterisk, or fine print on an image. The fix is to remove the item from the picture, not to disclaim it, unless the user wants the disclaimer.
- Break up monotony: do not run five fried-food images in a row. Alternate fried, healthy, fried.
- Avoid obvious AI: toy-looking food, plastic-looking kids, pizza that looks like a cartoon. Customers spot it and it kills trust.
- Pets: use labs, golden retrievers, dalmatians. Never pit bulls or German shepherds (stigma). Use common-looking dogs.
- Amazon OCR reads text on images and Alexa cites it as proof. Text on images is SEO. Put the real claims in real words.
- If a great image is sitting in A+ (the "nice to know") and not in the stack (the "need to know"), move it up. Buyers may never scroll to A+.
- A big value prop buried as the last image belongs near the top.

### Step 6. Write the fix briefs
Produce one brief per image, in slot order, using the exact template in `references/report_template.md`. Each brief is written so a designer or an image AI (Codex, ChatGPT image model) can execute it without asking a question: headline text, sub text, what the product is doing, setting, what to remove, and the brand lockup to use.

When you do not know the real-world use cases for a spec range (what do I cook at 260F vs 430F), ask an AI for four concrete examples spread across the range, then turn that into one four-panel infographic brief. Do not invent product capabilities; confirm anything the product may not actually do (can it really bake a quiche?) with the user before putting it in a brief.

### Step 7. Rollout plan (only if asked, or if the catalog has siblings)
If the product has 5+ siblings (20 air fryers, 10 pizza makers), write the rollout rule: what is locked identically across all siblings, and what adapts per unit (2 baskets becomes 3 baskets, 4.4 qt becomes 3 qt each with the new total). Fix one perfectly, then scale.

## Output format

ALWAYS use the structure in `references/report_template.md`. Bottom line first: the one-paragraph verdict and the top 3 fixes, then the hero scorecard, then the per-image stack table, then the briefs, then rollout. Deliver as a .md or .docx file when the user will share it with a buyer or designer; answer inline in chat for a quick single-image check.

Never use em dashes anywhere in the output. Plain language, fifth-grade reading level, concrete examples. Be blunt about what is wrong; the user wants honest challenge, not validation.

## Split-test guidance (when asked)
- Test pre-Amazon first (PickFu or Product Opinion) across the product line, not every SKU, to learn what wins before spending Amazon traffic.
- A 4-week on-Amazon test is usually too short to be conclusive.
- Testing bad image vs bad image produces a "winning bad image". Always test against a version that fixes the top finding of this audit, not just a variant of the current image.
- Ideas worth testing for food products: pepperoni vs cheese on the pizza, fried vs healthy in the air fryer basket.

## Brand kit lookup
Before writing briefs, read the brand kit for the product's brand at `../../../brand-kits/<brand>/BRAND.md` (relative to this skill; in the repo it is `brand-kits/pyle/BRAND.md`, with logo and trust stamp files in `brand-kits/pyle/assets/`). Put the exact hex codes, font names, logo file path, and the locked stack layout from that file into every brief so a designer or image AI produces on-brand output without guessing. All five brands (Pyle, SereneLife, NutriChef, Hurtle, Squatz) have kits. Pyle Pro and Pyle Vintage use the Pyle kit with the sub-brand lockup from the Pyle PDF. If a brand has no kit, say so under "Open questions" and write the briefs with neutral colors marked "replace with brand kit".

## Time expectation
A full stack redo with AI tooling is about 15 minutes for one listing once the brand kit (colors, fonts, lockup, image style) is defined. Without a brand kit, every listing drifts. Pyle's kit is in `brand-kits/pyle/BRAND.md`. For brands without a kit, say so and list what is needed (see `references/rules.md`, "Brand kit").
