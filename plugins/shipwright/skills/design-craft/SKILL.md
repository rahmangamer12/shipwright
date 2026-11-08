---
name: design-craft
description: Make client websites and UI look intentionally designed instead of AI-generated — typography, spacing scale, colour, layout, imagery and motion rules, plus how to faithfully match a client's mockup or brand. Use while designing or building any page, landing page, dashboard or redesign, or when the user says it looks generic, cheap, "AI jaisa", or not like the reference.
---

# Design craft

## If the client gave a design: match it, don't improve it
Measure from the mockup (font sizes, line heights, spacing, colours with an eyedropper/the image itself, border radius, shadows). Same section order, same copy. Your taste only fills gaps the mockup does not cover. Verify with `design-qa --ref`.

## If you are designing
1. **Pick a direction in one line** before coding: audience, mood, one reference style (e.g. "editorial, warm neutrals, serif headlines, for a family law firm"). Everything follows it.
2. **Type:** max 2 families. Headline font with character (serif or distinctive grotesk), body font highly readable at 16–18 px, line-height 1.5–1.7, measure 50–75 ch. Use a modular scale (1.2–1.333). Tight letter-spacing on large headings (-0.01 to -0.03em).
3. **Spacing:** 4/8 px scale only. Generous section padding (80–128 px desktop, 48–72 mobile). Group related items tighter than unrelated ones.
4. **Colour:** 1 brand colour + neutrals + 1 accent at most. Neutrals slightly tinted toward the brand hue (not pure grey). Check AA contrast. Define tokens as CSS variables.
5. **Layout:** a real grid (12-col or fixed content width ~1120–1280 px). Vary section layouts (split, full-bleed image, cards, quote) — never 6 identical centred blocks in a row. Left-align body text.
6. **Imagery:** real photos/product shots from the client first; otherwise consistent illustration or photo style. Never mix styles. No generic stock "handshake" unless asked.

## Avoid the "AI-generated" look
- Purple-to-blue gradients on everything, glassmorphism cards, glowing blobs
- Emoji as icons; three identical feature cards with icons in circles as the only layout
- Every heading centred with a gradient word; "Unlock the power of…", "Elevate your…", "Seamless" copy
- Random border radii and shadows; more than two button styles
- Inter-everywhere with no hierarchy; tiny grey body text
- Fake stats/testimonials/logos — never invent client facts; use clearly marked placeholders and list them in the handoff

## Motion
Subtle and purposeful: 150–250 ms ease-out for UI, small fade/translate on scroll at most, respect `prefers-reduced-motion`. No parallax or auto-playing carousels unless the brief asks.

## Final self-check
Squint test (is the hierarchy obvious?), grayscale test (does it still read?), mobile thumb test (can you use it one-handed?), and "would the client recognise their brand?"
