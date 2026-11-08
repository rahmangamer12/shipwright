---
name: wordpress
description: Deliver WordPress client work — build or rebuild pages from a brief or HTML design in Elementor, Divi, Gutenberg or a custom theme, fix sites, set up WooCommerce, SEO and speed — safely and verifiably. Use when the job mentions WordPress, WP, Elementor, Divi, WooCommerce, a theme or plugin zip, or a live WordPress site URL.
---

# WordPress playbook

## Decide how you will touch the site
- **Live site with a management tool installed** (e.g. the user has the `novamira` or `html-to-divi` skill, WP-CLI over SSH, or an MCP server for the site): use that tool. Read its instructions first.
- **Theme/plugin zip only:** work on files locally; test in a local WordPress if available (`wp-env`, LocalWP, Docker `wordpress` image). Never edit production files you cannot back up.
- **No access yet:** ask for exactly what you need (admin user or application password, hosting/SFTP, or a staging site). Never ask for the client's personal email password.

## Safety
- Back up before changes: export the affected posts/options, or note old values in the job's `qa/build-log.md`. Prefer staging.
- Install plugins only from wordpress.org or the vendor; never nulled/cracked themes or plugins.
- After changes purge every cache layer (plugin cache, server cache, CDN) before checking.

## Building pages from a design
1. Map each section of the design to the builder's native blocks/modules (Elementor containers, Divi sections/rows/modules, Gutenberg groups/columns). Use global colours and fonts from the design — set them once in the theme/builder globals.
2. Header/footer via the theme builder (Elementor Theme Builder, Divi Theme Builder, block theme template parts) with a real WP menu, not hard-coded links.
3. Images to the Media Library with alt text; compress (WebP).
4. Forms with the site's form plugin, test that submissions arrive.
5. Responsive: set tablet/mobile values explicitly; check them with `design-qa`.

## Baseline for every WP delivery
Site title/tagline/favicon set · permalinks "post name" · SEO plugin titles + meta for key pages · XML sitemap reachable · SSL + no mixed content · 404 page exists · contact form works · admin email is the client's · unused plugins/themes removed · caching enabled.

## Verify
Run `design-qa` on every built page at the live/staging URL (use `--headed` if the host blocks headless browsers), compare with the client's design using `--ref`, then hand off with login notes (never put passwords in HANDOFF.md — say where they were shared).
