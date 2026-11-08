"""Screenshot a page at 3 widths, run automated design/UX checks, optionally diff against a reference.

usage: python -P shots.py <url | local .html> --out <folder> [--ref <url | .html | .png>] [--headed] [--widths 375,768,1440]
Needs: pip install playwright pillow && python -m playwright install chromium
"""
import argparse, json, os, pathlib
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CHECKS_JS = r"""
() => {
  const out = {overflow: [], brokenImages: [], noAlt: [], lowContrast: [], smallTargets: [], badLinks: [], placeholder: [], headings: {}, meta: {}};
  const W = document.documentElement.clientWidth;
  const sel = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0,2).join('.') : '');
  out.pageScrollWidth = document.documentElement.scrollWidth; out.viewport = W;
  if (document.documentElement.scrollWidth > W + 1) {
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width && (r.right > W + 1 || r.left < -1) && getComputedStyle(el).position !== 'fixed') { out.overflow.push(sel(el) + ` (${Math.round(r.left)}..${Math.round(r.right)})`); if (out.overflow.length > 15) break; }
    }
  }
  for (const img of document.images) {
    if (img.complete && img.naturalWidth === 0 && img.src) out.brokenImages.push(img.src.slice(0,150));
    if (!img.hasAttribute('alt')) out.noAlt.push(img.src.slice(0,150));
  }
  const lum = c => { const m = c.match(/[\d.]+/g); if (!m) return null; const [r,g,b] = m.slice(0,3).map(v => { v/=255; return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); }); return {L: .2126*r+.7152*g+.0722*b, a: m[3] === undefined ? 1 : +m[3]}; };
  const bgOf = el => { while (el) { const s = getComputedStyle(el); if (s.backgroundImage !== 'none') return null; const l = lum(s.backgroundColor); if (l && l.a > .9) return l; el = el.parentElement; } return lum('rgb(255,255,255)'); };
  let n = 0;
  for (const el of document.querySelectorAll('p,li,a,span,h1,h2,h3,h4,h5,h6,button,label,td,th')) {
    if (n > 400) break;
    const t = [...el.childNodes].filter(x => x.nodeType === 3).map(x => x.textContent.trim()).join('');
    if (!t || el.offsetParent === null) continue; n++;
    const s = getComputedStyle(el), fg = lum(s.color), bg = bgOf(el); if (!fg || !bg) continue;
    const ratio = (Math.max(fg.L, bg.L) + .05) / (Math.min(fg.L, bg.L) + .05);
    const big = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && +s.fontWeight >= 700);
    if (ratio < (big ? 3 : 4.5)) out.lowContrast.push(`${sel(el)} "${t.slice(0,40)}" ratio ${ratio.toFixed(2)}`);
  }
  out.lowContrast = out.lowContrast.slice(0, 25);
  if (W < 500) for (const el of document.querySelectorAll('a,button,input,select,[role=button]')) {
    const r = el.getBoundingClientRect(); if (r.width && r.height && (r.width < 24 || r.height < 24) && el.offsetParent !== null) out.smallTargets.push(`${sel(el)} ${Math.round(r.width)}x${Math.round(r.height)}`);
  }
  out.smallTargets = out.smallTargets.slice(0, 25);
  for (const a of document.querySelectorAll('a')) { const h = a.getAttribute('href'); if (h === null || h === '' || h === '#' || h.startsWith('javascript:')) out.badLinks.push(`${sel(a)} "${a.textContent.trim().slice(0,30)}" href=${h}`); }
  out.badLinks = out.badLinks.slice(0, 25);
  const body = document.body.innerText;
  for (const p of [/lorem ipsum/i, /dolor sit amet/i, /your (text|title|heading) here/i, /\bTODO\b/, /placeholder/i, /example\.com/i]) { const m = body.match(p); if (m) out.placeholder.push(m[0]); }
  const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => h.offsetParent !== null).map(h => +h.tagName[1]);
  out.headings = {h1Count: hs.filter(x => x === 1).length, skipped: hs.some((h,i) => i && h - hs[i-1] > 1), order: hs.slice(0,40).join('')};
  out.meta = {title: document.title, description: (document.querySelector('meta[name=description]')||{}).content || null, lang: document.documentElement.lang || null, viewport: !!document.querySelector('meta[name=viewport]'), favicon: !!document.querySelector('link[rel~=icon]'), ogImage: !!document.querySelector('meta[property="og:image"]')};
  out.fonts = [...new Set([...document.querySelectorAll('h1,h2,p,body')].map(e => getComputedStyle(e).fontFamily.split(',')[0].replace(/["']/g,'').trim()))];
  out.fontsFailed = [...document.fonts].filter(f => f.status === 'error').map(f => f.family);
  return out;
}
"""


def to_url(x):
    if x.startswith(("http://", "https://", "file:")):
        return x
    return pathlib.Path(x).resolve().as_uri()


def shoot(page, url, path, w):
    page.set_viewport_size({"width": w, "height": 900})
    page.goto(url, wait_until="load", timeout=60000)
    page.wait_for_timeout(800)
    page.evaluate("async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } window.scrollTo(0, 0); }")
    page.wait_for_timeout(600)
    page.screenshot(path=path, full_page=True)


def diff(ref_png, build_png, out_png):
    from PIL import Image, ImageChops
    a, b = Image.open(ref_png).convert("RGB"), Image.open(build_png).convert("RGB")
    w, h = max(a.width, b.width), max(a.height, b.height)
    A, B = Image.new("RGB", (w, h), "white"), Image.new("RGB", (w, h), "white")
    A.paste(a), B.paste(b)
    d = ImageChops.difference(A, B).convert("L").point(lambda v: 255 if v > 40 else 0)
    pct = 100 * d.histogram()[255] / (w * h)
    red = Image.new("RGB", (w, h), (255, 0, 64))
    over = Image.composite(red, Image.blend(B, Image.new("RGB", (w, h), "white"), .6), d)
    sheet = Image.new("RGB", (w * 3 + 40, h), (30, 30, 30))
    for i, im in enumerate((A, B, over)):
        sheet.paste(im, (i * (w + 20), 0))
    if sheet.height > 6000:
        sheet = sheet.crop((0, 0, sheet.width, 6000))
    sheet.save(out_png)
    return round(pct, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target"); ap.add_argument("--out", required=True); ap.add_argument("--ref")
    ap.add_argument("--headed", action="store_true"); ap.add_argument("--widths", default="375,768,1440")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    os.makedirs(a.out, exist_ok=True)
    report = {"target": a.target, "widths": {}}
    with sync_playwright() as p:
        args = ["--window-position=-2000,0"] if a.headed else []
        br = p.chromium.launch(headless=not a.headed, args=args)
        for w in [int(x) for x in a.widths.split(",")]:
            page = br.new_page()
            errors, failed = [], []
            page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)[:200]))
            page.on("requestfailed", lambda r: failed.append(r.url[:150]))
            page.on("response", lambda r: failed.append(f"{r.status} {r.url[:150]}") if r.status >= 400 else None)
            shot = os.path.join(a.out, f"build-{w}.png")
            shoot(page, to_url(a.target), shot, w)
            res = page.evaluate(CHECKS_JS)
            res["consoleErrors"], res["failedRequests"] = errors[:20], failed[:20]
            if a.ref:
                refshot = os.path.join(a.out, f"ref-{w}.png")
                if a.ref.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    from PIL import Image
                    im = Image.open(a.ref).convert("RGB")
                    im.resize((w, int(im.height * w / im.width))).save(refshot)
                else:
                    rp = br.new_page(); shoot(rp, to_url(a.ref), refshot, w); rp.close()
                res["refMismatchPct"] = diff(refshot, shot, os.path.join(a.out, f"compare-{w}.png"))
            report["widths"][w] = res
            page.close()
        br.close()
    json.dump(report, open(os.path.join(a.out, "report.json"), "w"), indent=2)
    print(f"QA for {a.target} -> {a.out}")
    for w, r in report["widths"].items():
        issues = {k: len(v) for k, v in r.items() if isinstance(v, list) and v and k != "fonts"}
        hd = r["headings"]
        flags = []
        if r["pageScrollWidth"] > r["viewport"] + 1: flags.append(f"H-SCROLL {r['pageScrollWidth']}>{r['viewport']}")
        if hd["h1Count"] != 1: flags.append(f"H1 x{hd['h1Count']}")
        if hd["skipped"]: flags.append("heading levels skipped")
        if not r["meta"]["description"]: flags.append("no meta description")
        if "refMismatchPct" in r: flags.append(f"ref mismatch {r['refMismatchPct']}%")
        print(f"  {w}px: {issues or 'no list issues'} {'; '.join(flags)}")
    print("Open the PNGs with the Read tool for the visual review; details in report.json")


if __name__ == "__main__":
    main()
