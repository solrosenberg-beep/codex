# Session 2 rules (John Aspinall, L10 Sales Team, Nov 2 2026)

Read this after `rules.md`. These are the rules John added or sharpened in the second session, based on live teardowns of a camping toilet, a super-cardioid mic, a digital toaster, a vacuum sealer, and a curb ramp. Where this file and `rules.md` overlap, this one is the newer and more specific version.

## 1. Avatar first, then pain, then image

Before any brief, answer in writing: who is the buyer, and what is the pain that made them search?
- Camping toilet: a heavy adult who is afraid it will collapse under them. Not "a camper."
- Vacuum sealer: someone who buys in bulk at Costco and hates throwing out food. It is a money-saving device, not a food-prep device.
- Curb ramp: owners of lowered or luxury cars who scrape the front bumper, valet businesses, schools and lots. Not "grandpa with a walker."
- Car phone holder: Uber and DoorDash drivers who must see the app. Not "everyone with a phone."
- Live mic: live performance, karaoke, school events, PA. Not podcasting (no USB).

The hero and slot 2 speak to that avatar's pain. Secondary uses (toilet as a stool, sealer for wine bottles, ramp for a walker) go last or get cut. Nobody buys the primary product for the secondary use.

## 2. Show the pain, not just the product

Before/after is the strongest format when the pain is visual: a bumper scraping the curb, brown lettuce in the fridge, burnt toast from guessing a number. Show the problem first, then the product fixing it. If the listing never shows the pain, the buyer has no reason to care.

## 3. The avatar is the model in the photo

Cast the person in the lifestyle shots to match the buyer, consistently across the whole stack. For a 330 lb capacity toilet, the model is a big guy in every image, not a skinny one. Skinny buyers reason "if it holds him it holds me." Big buyers see themselves. One avatar, every image.

## 4. Count everything. Put the number on the image.

Counts are value props and buyers compare them: 10 bags, 48 wipes, 15 ft cable, 6 preset modes, 2 colors, 330 lb. If a number is missing (how many bags?) the buyer assumes the worst. Rank the numbers by what decides the purchase (bags beat wipes, capacity beats both) and put the biggest one on the hero.

## 5. Read the competitor signals on the SERP

Every call still starts on the search results page. Look for:
- A callout a competitor uses that you don't (weight capacity on the toilets). That is a question buyers ask. Answer it.
- A feature a competitor has that you don't (touchscreen on toasters). That is a signal to sell why not having it is better ("no fiddly screen, pick the toast color"), as long as nothing else in the catalog has that feature.
- A format the category allows (lifestyle heroes in automotive). Test it.
- What everyone shows (steak and vegetables on every sealer). That is table stakes. Do it, but it is not your differentiator.

## 6. Show the biggest thing it fits, not the smallest

Toaster: show a bagel or a Belgian waffle, not two slices of plain toast. If it fits the big thing it fits the small thing. Pick the largest realistic item for the category and split test it.

## 7. Translate controls into outcomes

"Levels 1 through 6" means nothing. "Pick the color of toast you want" is the whole product. When a product replaces guessing with a visual choice, say so and show the competitor's confusing version next to it. Name modes by what they do: "6 visual toast modes," not "6 presets."

## 8. Realism checks that fail most often

- Where is it plugged in? Show the outlet, the cord length, and that the cord clears the hot metal.
- Scale: a toaster in the middle of a kitchen island looks huge and fake. Put it under a cabinet next to a utensil holder.
- The bag in the lifestyle photo must be the same bag that ships.
- Collapsed vs expanded: use arrows and labels so a collapsed product is not mistaken for a lid.
- Two listings of the same product must have the same product shape in their images. If they differ, one is wrong.
- Mixing uses that disgust: do not show fish in a product someone uses as a toilet.
- Do not vacuum-seal grapes, chips, or tomatoes in the photos. Seal steak, chicken, fish, pork, and the vegetables that actually go bad fast (lettuce, spinach, berries, herbs). Ask an AI for the top 25 fastest-spoiling groceries and pick the most visible ones.

## 9. Adjustable ranges need real-world anchors

"4 in to 15.9 in" is a spec, not a message. Show an adult at the adult height and a kid at the kid height. If the low number is just the collapsed size, say "packs down to 4 in," not "adjusts to 4 in."

## 10. Save-money math on the image

For bulk or waste-reduction products, do the math on the image: "Single steak $7.49. Bulk pack per steak $3. Seal the rest." Buyers believe a number more than an adjective.

## 11. Side merchandising decides the hero angle

If you will put a label on the side of the product (toaster side panel), shoot the angle that shows that side. If you will not, shoot straight on or slightly aerial. The angle serves the message.

## 12. Commoditized electronics: us vs them with 3 to 4 rows

For mics, cables, speakers: pick 3 or 4 real differences (15 ft vs 9 ft cable, on/off switch, feedback suppression, US warranty, US support) and put them in one us-vs-them image. If nothing technical differs, US company and US warranty still decommoditize.

## 13. Break out one use case into five

"Live performance" becomes rock show, school play, community event, outdoor event, karaoke night. Let search query performance decide which two or three go on the images. If the product cannot do a use (no USB means no podcast), it does not appear anywhere.

## 14. Brand family image must feel like a catalog

A "trusted brand for 60 years" image with 5 products does not say "huge catalog." Show a wall of products, not a handful.

## 15. Cards are segmentation; integrate the message into the scene

Electronics stacks often use a photo on one side and a "card" with text on the other. Avoid it. Put the headline in the scene so the image reads as one thing, not two.

## 16. Compliance warnings

- Curb ramps: do not show bolting into a public street as the default. Call out the avatar (private driveway, lot owner, valet) and show the no-drill use first.
- AI-generated UGC-style video must be labeled AI in metadata (New York, federal direction). Prefer real iPhone footage edited by AI.

## 17. QA gate before a human looks at it

John runs every finished stack through a scorer (Jev / TypeSafe image classifier) that grades each image on: infographic vs lifestyle, mobile readability, benefit stated, cleanliness, on-brand, looks AI. Cost is near zero per stack. Nothing goes to a human reviewer until it passes. Our rebuild skill does the same with its own checklist; when a TypeSafe or similar classifier is available, use it as the gate and feed failures back into regeneration before showing the set.

## 18. Tools John mentioned

- Jev / TypeSafe: classifier, not a chat model. Yes/no, good/bad scoring at near-zero cost. Now scores images.
- Grokbot: agent platform; a shared org bot so every buyer works the same way.
- Claude 3D render from one hero image plus the link: a rough 3D model to feed video generators so they understand the product's parts.
- Codex as a video editor: cut real iPhone and customer videos plus royalty-free stock B-roll into Sponsored Brand video.
- Pre-Amazon split testing still applies (see `rules.md`).
