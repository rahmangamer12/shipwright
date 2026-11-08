---
name: nextjs
description: Build or convert client work into a production-grade Next.js (App Router) site or app — from a brief, a mockup, or an existing HTML/CSS/React project — with Tailwind, typed code, SEO, accessibility and a clean build. Use when the brief says Next.js/React/modern web app, when converting a static HTML template to Next.js, or when no stack is given for an interactive web app.
---

# Next.js playbook

## Setup
- Check the installed toolchain first: `node -v` (need 20+). Check the current Next.js major with `npm view next version` — never assume APIs from memory; read `node_modules/next/dist/docs` or the official docs for anything version-sensitive.
- Scaffold: `npx create-next-app@latest build --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes` (inside the job folder). If the client sent an existing project, work in a copy of it instead and keep their structure.

## Converting HTML/CSS to Next.js
1. Inventory sections of each HTML page → one component per section in `src/components/sections/`.
2. Move global CSS variables/fonts into `globals.css` + `next/font`; keep the client's class names only if they asked for "same code", otherwise translate to Tailwind faithfully (same spacing, colours, sizes — measure, don't guess).
3. Images → `public/` and `next/image` with explicit width/height; keep original alt text or write real alt text.
4. Every `<a href="page.html">` → `next/link` route. Forms → a Server Action or route handler with validation (zod) and a visible success/error state.
5. JS from the template (sliders, menus) → small client components (`"use client"`) or remove if CSS can do it. No jQuery unless the brief demands it.

## Quality rules
- Server Components by default; `"use client"` only where state/effects/browser APIs are needed.
- `metadata` / `generateMetadata` per route (title, description, Open Graph), `app/sitemap.ts`, `app/robots.ts`, `app/icon.*`.
- Accessible: semantic landmarks, one H1 per page, labelled inputs, focus-visible styles, `prefers-reduced-motion` respected for animations.
- Content in data files (`src/content/*.ts`) not hard-coded in JSX, so the client can edit text easily.
- No secrets in client code; env vars in `.env.local` with `.env.example` committed.
- Dark mode only if the brief asks or the design has it.

## Gates (must pass before handoff)
```
npm run lint
npx tsc --noEmit
npm run build
```
All exit 0. Then `npm run start -- -p 3123` and run the `design-qa` skill against `http://localhost:3123/<each route>`. Add a README with: install, dev, build, deploy (Vercel: import repo → deploy; or `npm run build && npm start` on a Node host), and where to edit content.
