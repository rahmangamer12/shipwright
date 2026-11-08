"""Package a finished build into a client-ready zip with a manifest and a secret scan.

usage: python -P package.py <build folder> <output .zip>
Excludes node_modules, .git, .next, dist caches, __pycache__, .env files (keeps .env.example).
Exit code 2 if likely secrets were found (fix them before sending).
"""
import hashlib, os, re, sys, zipfile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SKIP_DIRS = {"node_modules", ".git", ".next", ".turbo", ".vercel", "__pycache__", ".cache", ".parcel-cache", ".DS_Store"}
SECRET = re.compile(
    r"(sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{36}|"
    r"xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"(?i:(password|passwd|secret|api_key|apikey|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]))"
)
TEXT_EXT = {".js", ".ts", ".tsx", ".jsx", ".json", ".php", ".py", ".env", ".yml", ".yaml", ".md", ".html", ".css", ".txt", ".ini", ".xml", ".mjs", ".cjs"}


def skip_file(name):
    n = name.lower()
    return (n.startswith(".env") and n != ".env.example") or n in {".ds_store", "thumbs.db"}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rows, hits = [], []
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for r, ds, fs in os.walk(src):
            ds[:] = sorted(d for d in ds if d not in SKIP_DIRS)
            for f in sorted(fs):
                p = os.path.join(r, f)
                if skip_file(f) or os.path.abspath(p) == out:
                    continue
                rel = os.path.relpath(p, src).replace(os.sep, "/")
                data = open(p, "rb").read()
                if os.path.splitext(f)[1].lower() in TEXT_EXT and len(data) < 2_000_000:
                    for m in SECRET.finditer(data.decode("utf8", "ignore")):
                        hits.append(f"{rel}: {m.group(0)[:12]}…")
                z.writestr(rel, data)
                rows.append(f"{hashlib.sha256(data).hexdigest()[:16]}  {len(data):>10}  {rel}")
        z.writestr("MANIFEST.txt", "sha256(16)        bytes  path\n" + "\n".join(rows) + "\n")
    print(f"packaged {len(rows)} files -> {out} ({os.path.getsize(out)/1e6:.2f} MB)")
    if hits:
        print("\nPOSSIBLE SECRETS — remove before sending:")
        print("\n".join("  " + h for h in hits[:50]))
        sys.exit(2)
    print("secret scan: clean")


if __name__ == "__main__":
    main()
