"""Build dist/: one all-in-one 'shipwright' skill zip (for claude.ai / Desktop / Cowork) + the plugin zip."""
import json, os, re, shutil, zipfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(R, "plugins", "shipwright", "skills")
OUT = os.path.join(R, "dist"); STAGE = os.path.join(OUT, "shipwright")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(os.path.join(STAGE, "references")); os.makedirs(os.path.join(STAGE, "scripts"))
body = lambda p: re.sub(r"^---.*?---\s*", "", open(p, encoding="utf8").read(), flags=re.S)
main = body(os.path.join(SK, "deliver", "SKILL.md"))
for a, b in [
    ("Pick the playbook by project type and load that skill:", "Pick the playbook by project type and read that reference file:"),
    ("→ `nextjs` skill", "→ read `references/nextjs.md`"),
    ("→ `wordpress` skill", "→ read `references/wordpress.md`"),
    ("then use `design-craft`", "then follow `references/design-craft.md`"),
    ("apply `design-craft` rules", "apply `references/design-craft.md` rules"),
    ("load the `design-qa` skill and run it", "follow `references/design-qa.md`"),
    ("`shots.py` in the design-qa skill also needs", "`shots.py` also needs"),
    ("Helper scripts live in `scripts/` next to this file", "Helper scripts live in `scripts/` in this skill's folder"),
]:
    main = main.replace(a, b)
desc = ("Shipwright: brief in, finished work out. ALWAYS use this skill when the user types the word \"shipwright\" "
        "(alone, as /shipwright, or with a file, zip, link or pasted brief), and whenever they hand over a client job "
        "(brief, zip, folder, mockup, reference site or requirements) and want it built: websites, Next.js, WordPress, "
        "Elementor, Divi, HTML/CSS, landing pages, documents. Runs intake, a requirement checklist, only blocking questions, "
        "the build, design QA at mobile/tablet/desktop, an independent requirement audit and a client-ready zip with a handoff note.")
head = "---\nname: shipwright\ndescription: " + json.dumps(desc, ensure_ascii=False) + "\n---\n\n"
trigger = ("## Command\n\nWhen the user's message is just `shipwright` (or `/shipwright`) with no files or brief, reply with one short line "
           "asking them to attach the client's zip/brief or paste the requirements. When files or a brief are present, start Phase 1 immediately.\n\n")
main = main.replace("# Shipwright — Deliver\n", "# Shipwright\n\n" + trigger, 1)
open(os.path.join(STAGE, "SKILL.md"), "w", encoding="utf8").write(head + main)
for f in os.listdir(os.path.join(SK, "deliver", "references")):
    shutil.copy(os.path.join(SK, "deliver", "references", f), os.path.join(STAGE, "references", f))
for name in ["design-qa", "design-craft", "nextjs", "wordpress"]:
    t = body(os.path.join(SK, name, "SKILL.md")).replace("`scripts/` is next to this file", "`scripts/` is in the skill's root folder")
    t = t.replace("run the `design-qa` skill", "follow `references/design-qa.md`").replace("use `design-qa`", "follow `references/design-qa.md`").replace("with `design-qa`", "with `references/design-qa.md`").replace("Run `design-qa`", "Follow `references/design-qa.md`")
    open(os.path.join(STAGE, "references", name + ".md"), "w", encoding="utf8").write(t)
for d in ["deliver", "design-qa"]:
    for f in os.listdir(os.path.join(SK, d, "scripts")):
        if f.endswith(".py"):
            shutil.copy(os.path.join(SK, d, "scripts", f), os.path.join(STAGE, "scripts", f))
def zipdir(src, out, prefix):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for r, ds, fs in os.walk(src):
            ds[:] = [x for x in ds if x != "__pycache__"]
            for f in fs:
                p = os.path.join(r, f); z.write(p, os.path.join(prefix, os.path.relpath(p, src)).replace(os.sep, "/"))
zipdir(STAGE, os.path.join(OUT, "shipwright.zip"), "shipwright")
zipdir(os.path.join(R, "plugins", "shipwright"), os.path.join(OUT, "shipwright-plugin.zip"), "")
print("built", [f for f in os.listdir(OUT) if f.endswith(".zip")], "desc chars:", len(desc))
