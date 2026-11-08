"""Safely unpack a client job (zip, folder or single file) and print an inventory.

usage: python -P unpack.py <input: .zip | folder | file> <dest folder>
- Zips are extracted with path-traversal, symlink and size checks (nested zips too, one level).
- .docx / .pdf / .html text is extracted to <dest>/_text/ so briefs are easy to read.
- Prints counts by type, a short tree and a project-type guess.
"""
import os, re, shutil, sys, zipfile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from collections import Counter

MAX_TOTAL = 2 * 1024**3   # 2 GB uncompressed
MAX_FILES = 20000


def safe_extract(zpath, dest):
    dest_real = os.path.realpath(dest)
    with zipfile.ZipFile(zpath) as z:
        infos = z.infolist()
        if len(infos) > MAX_FILES:
            sys.exit(f"refused: {len(infos)} entries in {zpath}")
        if sum(i.file_size for i in infos) > MAX_TOTAL:
            sys.exit(f"refused: {zpath} expands beyond 2 GB")
        for i in infos:
            name = i.filename.replace("\\", "/")
            if name.startswith("/") or re.match(r"^[A-Za-z]:", name) or ".." in name.split("/"):
                print(f"  skipped unsafe path: {name}")
                continue
            if (i.external_attr >> 16) & 0o170000 == 0o120000:
                print(f"  skipped symlink: {name}")
                continue
            target = os.path.realpath(os.path.join(dest, name))
            if not target.startswith(dest_real + os.sep) and target != dest_real:
                print(f"  skipped escaping path: {name}")
                continue
            if name.endswith("/"):
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(i) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)


def docx_text(p):
    try:
        with zipfile.ZipFile(p) as z:
            xml = z.read("word/document.xml").decode("utf8", "ignore")
        xml = re.sub(r"</w:p>", "\n", xml)
        return re.sub(r"<[^>]+>", "", xml)
    except Exception as e:
        return f"[could not read docx: {e}]"


def pdf_text(p):
    try:
        from pypdf import PdfReader
        return "\n\n".join((pg.extract_text() or "") for pg in PdfReader(p).pages)
    except ImportError:
        return "[pypdf not installed: pip install pypdf — or open the PDF with the Read tool]"
    except Exception as e:
        return f"[could not read pdf: {e}]"


def html_text(p):
    s = open(p, encoding="utf8", errors="ignore").read()
    comments = re.findall(r"<!--(.*?)-->", s, re.S)
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if comments:
        s += "\n\nHTML COMMENTS:\n" + "\n".join(c.strip() for c in comments if c.strip())
    return s


def guess(files, root):
    names = {os.path.basename(f).lower() for f in files}
    rel = [os.path.relpath(f, root).replace("\\", "/").lower() for f in files]
    g = []
    pkg = [f for f in files if os.path.basename(f) == "package.json" and "node_modules" not in f]
    for p in pkg:
        t = open(p, encoding="utf8", errors="ignore").read()
        g.append("Next.js app" if '"next"' in t else "Vite/React app" if "vite" in t else "Node project")
    if any("wp-content" in r for r in rel) or "functions.php" in names:
        g.append("WordPress theme/plugin/site")
    if any(r.endswith("style.css") and "theme name:" in open(f, encoding="utf8", errors="ignore").read(2000).lower() for f, r in zip(files, rel)):
        g.append("WordPress theme")
    if "index.html" in names and not pkg:
        g.append("Static HTML/CSS site")
    if any(n.endswith((".fig", ".psd", ".sketch", ".xd", ".ai")) for n in names):
        g.append("Design source files (needs export to images)")
    if any(n.endswith((".docx", ".pdf", ".txt", ".md")) for n in names):
        g.append("Written brief / documents present")
    return sorted(set(g)) or ["Unknown — read files manually"]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dest = sys.argv[1], sys.argv[2]
    os.makedirs(dest, exist_ok=True)
    if os.listdir(dest):
        sys.exit(f"refused: {dest} is not empty (use a new folder per job)")
    if os.path.isdir(src):
        shutil.copytree(src, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("node_modules", ".git"))
    elif zipfile.is_zipfile(src):
        safe_extract(src, dest)
    else:
        shutil.copy2(src, dest)
    for r, _, fs in os.walk(dest):  # nested zips, one level
        for f in fs:
            p = os.path.join(r, f)
            if f.lower().endswith(".zip") and zipfile.is_zipfile(p):
                out = p[:-4]
                if not os.path.exists(out):
                    os.makedirs(out)
                    safe_extract(p, out)
                    print(f"  unpacked nested zip: {os.path.relpath(p, dest)}")
    files = [os.path.join(r, f) for r, ds, fs in os.walk(dest) for f in fs if "_text" not in r]
    tdir = os.path.join(dest, "_text")
    for f in files:
        low = f.lower()
        fn = {".docx": docx_text, ".pdf": pdf_text, ".html": html_text, ".htm": html_text}.get(os.path.splitext(low)[1])
        if fn:
            os.makedirs(tdir, exist_ok=True)
            name = os.path.relpath(f, dest).replace(os.sep, "__") + ".txt"
            open(os.path.join(tdir, name), "w", encoding="utf8").write(fn(f))
    exts = Counter(os.path.splitext(f)[1].lower() or "(none)" for f in files)
    print(f"\nFILES: {len(files)}  SIZE: {sum(os.path.getsize(f) for f in files)/1e6:.1f} MB")
    print("TYPES: " + ", ".join(f"{e}:{c}" for e, c in exts.most_common(15)))
    print("PROJECT TYPE: " + "; ".join(guess(files, dest)))
    print("\nTREE (depth 3):")
    for r, ds, fs in os.walk(dest):
        depth = os.path.relpath(r, dest).count(os.sep) + (0 if r == dest else 1)
        ds[:] = sorted(d for d in ds if d not in ("node_modules", ".git"))
        if depth > 3:
            ds[:] = []
            continue
        print("  " * depth + (os.path.basename(r) + "/" if r != dest else "./"))
        for f in sorted(fs)[:25]:
            print("  " * (depth + 1) + f)
        if len(fs) > 25:
            print("  " * (depth + 1) + f"... +{len(fs)-25} more")
    if os.path.isdir(tdir):
        print(f"\nText extracts written to {tdir} — read them all.")


if __name__ == "__main__":
    main()
