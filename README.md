# Shipwright — brief in, finished work out

A Claude Code plugin for freelancers and agencies. Hand it a client brief, a zip or a project folder; it:

1. **Unpacks safely** and reads everything (docx/pdf briefs, mockups, HTML, code)
2. **Writes a SPEC checklist** — every requirement numbered and testable, plus a professional baseline
3. **Asks only blocking questions**, once, then records sensible defaults
4. **Builds** with the right playbook — Next.js, WordPress (Elementor/Divi/Gutenberg), static HTML, documents
5. **Checks the design** at mobile/tablet/desktop (overflow, contrast, broken images, tap targets, placeholder text, SEO basics) and diffs against the client's reference
6. **Audits independently** — a separate agent verifies each requirement with evidence
7. **Packages** a client-ready zip with a manifest, secret scan and a HANDOFF.md

## Install

In Claude Code:

```
/plugin marketplace add rahmangamer12/shipwright
/plugin install shipwright@shipwright
```

Local copy (no GitHub):

```
/plugin marketplace add "F:/path/to/Shipwright"
/plugin install shipwright@shipwright
```

One-time for design QA screenshots:

```
pip install playwright pillow pypdf
python -m playwright install chromium
```

## Use

```
/shipwright:deliver C:/Downloads/client-brief.zip
```

Or just drop the zip/brief in chat and say "deliver this". Other skills you can call directly:

| Skill | What it does |
|---|---|
| `/shipwright:deliver` | Full job: intake → spec → questions → build → QA → handoff |
| `/shipwright:design-qa` | Find visual/UX bugs on any URL or HTML file, compare to a reference |
| `/shipwright:design-craft` | Rules for designs that don't look AI-generated, or matching a mockup |
| `/shipwright:nextjs` | Next.js App Router build/convert playbook with quality gates |
| `/shipwright:wordpress` | WordPress/Elementor/Divi delivery playbook |

Agent: `brief-auditor` — independent PASS/FAIL audit of SPEC.md vs the build.

Output lands in `jobs/<job-name>/` → `delivery/<job-name>.zip` + `HANDOFF.md`.

## License
MIT
