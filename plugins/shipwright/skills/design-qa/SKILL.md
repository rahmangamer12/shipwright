---
name: design-qa
description: Catch visual and UX bugs in a website or web app before a client sees them — layout overflow, broken images, low contrast, tiny tap targets, missing alt text, console errors, placeholder content, heading problems — at mobile, tablet and desktop widths, and compare against a reference design. Use after building or changing any page, when asked to "check the design", "find UI bugs", "is it pixel perfect", "compare with the mockup", or before delivering web work.
argument-hint: "<url or local html path> [--ref <reference url/html/image>]"
---

# Design QA

Two layers: an automated scan (fast, objective) and a visual review by you (taste, alignment, brand). Both are required; the scan alone misses ugly-but-valid layouts.

## 1. Automated scan

```
python -P scripts/shots.py <url-or-file> --out <job>/qa/<page-name> [--ref <reference url/file/png>] [--headed]
```
(`scripts/` is next to this file. Needs `pip install playwright pillow` and `python -m playwright install chromium` once. For a Next.js/Vite project start the dev or preview server first and pass `http://localhost:PORT/path`. Use `--headed` if a host/CDN challenge blocks headless browsers.)

It writes, per width (375, 768, 1440): a full-page PNG, and `report.json` with findings. With `--ref` it also writes `compare-<w>.png` (reference | build | diff) and a mismatch %.

Checks: horizontal overflow and the elements causing it · broken images · images without alt · text contrast below WCAG AA · tap targets < 24 px (mobile) · `href="#"`/empty links · lorem ipsum/placeholder text · missing/duplicate H1 and skipped heading levels · missing title/meta description · console errors and failed requests · fonts falling back.

**If the scan cannot run** (claude.ai/Desktop chat without a browser, no Playwright): try `pip install playwright pillow && python -m playwright install chromium` once; if that fails, review the HTML/CSS source against the same checklist (fixed widths > 375px, images without alt, `href="#"`, lorem ipsum, colour pairs for contrast, heading order, meta tags) and ask the user for screenshots at mobile and desktop width. Say clearly in the report that the scan was manual.

## 2. Visual review (you)

Open every screenshot with the Read tool and look like a picky client. Check:
- **Alignment & rhythm:** consistent left edges, equal gutters, spacing on a scale (4/8 px), no orphan words in headings
- **Hierarchy:** one clear focal point per section; CTA obvious; body text 16–18 px, line length 50–80 chars
- **Consistency:** same button styles, radius, shadows, icon set and font weights everywhere
- **Mobile:** nav works, nothing cramped, images not cropped badly, sticky elements don't cover content
- **Reference match:** compare section order, colours, fonts, spacing, copy against the brief/mockup — list each difference
- **States:** hover/focus, empty/error/success states for forms, loading states

## 3. Report and fix

Write `qa/design-qa.md` with a table: Severity (Critical = broken/unusable, Major = clearly wrong vs brief or ugly, Minor = polish) · Page · Width · Issue · Fix. Fix all Critical and Major, re-run the scan, and only then mark the page done. Never call a page "pixel perfect" without a `--ref` comparison under ~5% mismatch plus your own visual check.
