# Brief template and prompt pattern

## Per-slot brief (fill one per image in briefs.md)

```
### Slot <NN>: <message in 5 words or fewer>   (replaces current image <NN>, output file <SKU>-<NN>.png)
- Source fact: <the line from facts.md this image is built on>
- Headline (exact text, max 5 words):
- Sub text (exact text, max 12 words):
- Big number (if any):
- What the product is doing:
- Setting: <room, surface, who is there, what food or scenario>  (must differ from every other slot: room, angle, background, model, dish)
- Camera angle: <front / three-quarter / top-down / close-up / wide>
- Disclaimers: none (never add "not included" or "sold separately" unless the user asked)
- Realism notes: <quantities, what must NOT appear>
- Must fill the frame: <the one element that is largest>
- Brand panel: <which hex background, which hex text, per BRAND.md approved pairs>
- Fonts: <headline font / body font from BRAND.md>
- Logo: <file path, position, size as fraction of width>
- Trust stamp: yes / no
- Uncertain: <anything the user must confirm, or "none">
```

## Scene list check

Before generating, write one line per slot: `NN: <room> / <angle> / <background color> / <who> / <food or object>`. Read the list top to bottom. If any two lines share three or more parts, change one of them.

## Prompt pattern for the image model

Keep the prompt concrete. Describe the scene like a photographer's shot list, then the graphic panel like a designer's spec. Example for a dual basket air fryer, slot 2:

```
Square 2000x2000 product infographic for an Amazon listing.
Scene: a matte black dual-basket air fryer, two drawers pulled halfway open, on a light wood kitchen counter, soft natural window light from the left, shallow depth of field, realistic. Left drawer holds a normal single serving of crispy fries. Right drawer holds four chicken wings. Nothing overflowing.
Graphic panel: a solid deep burgundy (#5C191D) band across the top 28% of the image. Inside it, large bold headline text in bright yellow (#FBEF56): "Two Baskets. One Meal." Below it, smaller white text: "4.4 qt + 4.4 qt = 8.8 qt total". The headline must be large enough to read when the image is shrunk to a 150 pixel thumbnail.
Leave the bottom left corner clear for a logo.
No other text, no watermarks, no extra logos, no people.
```

Notes:
- Give the model one scene and one panel. Not two scenes.
- Always state "realistic" and name the quantities.
- Always leave a clear logo zone; the logo is pasted in afterwards from the brand kit file.
- If the model mangles text, drop the text lines from the prompt, ask for an empty panel, and add the text with Pillow in the brand font.
- For us-vs-them: "split image, left half labeled area shows a cheap competitor result (<what fails>), right half shows ours (<what works>). Same lighting both sides."
- For dimensions in place: "the product sitting under a standard 18 inch upper kitchen cabinet with visible clearance above it" rather than numbers on white.

## Compose script expectations (compose.py)

Inputs: generated PNG, brief fields. Steps: open image, draw text with the brand font (fall back per BRAND.md if the font file is missing), paste logo PNG with alpha at the kit position, paste trust stamp if required, save. Also write a 150 px thumbnail next to the output as `<file>.thumb.png` so the readability check is one glance.
