# Professional baseline (add to every SPEC that fits)

Web (any stack)
- Responsive at 375, 768, 1440 px; no horizontal scroll; tap targets ≥ 24 px on mobile
- No broken images, links to `#`, lorem ipsum, or console errors
- Text contrast ≥ 4.5:1 (3:1 for large text); visible keyboard focus
- Every image has meaningful alt text; one H1 per page; logical heading order
- Title + meta description per page; favicon; Open Graph image for the home page
- Forms: labels, validation messages, success state, spam protection
- Fonts load without layout jump; images sized/optimised (WebP/AVIF where possible)
- Lighthouse (mobile) Performance ≥ 85, Accessibility ≥ 95, SEO ≥ 95 when measurable

Code
- Build/lint/type-check exit 0; no unused deps; no secrets in the repo; `.env.example` if env vars exist
- README with run/build/deploy steps

Documents
- Matches requested format and page size; consistent fonts/spacing; no spelling errors; client name spelled exactly as in the brief

WordPress
- Updates/plugins only from trusted sources; no nulled themes; caching purged after changes; admin email/branding set to the client
