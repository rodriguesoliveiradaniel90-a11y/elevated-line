#!/usr/bin/env python3
"""
build.py — bundles content/*.json into index.html → dist/index.html

Usage:
  python3 build.py                 # build dist/index.html
  python3 build.py --vocab-from-anki   # refresh content/vocab.json from Anki first (Anki must be open)

The template index.html has placeholders like __SCENARIOS__ inside
<script type="application/json"> tags. Each is replaced by the minified JSON, escaped to pure ASCII (\\uXXXX) so the page renders correctly whatever charset the host assumes.
"</script" sequences inside JSON strings are escaped so they can't close the tag.
No secrets, no API keys — the published page uses claude.use("sample") only.
"""
import json, os, re, sys, html, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "index.html")
OUT  = os.path.join(ROOT, "dist", "index.html")      # claude.ai artifact copy
SITE = os.path.join(ROOT, "site")                     # GitHub Pages / PWA copy
CLAUDE_URL = "https://claude.ai/code/artifact/025fdbf5-a9fc-41e5-84a3-71aff5161ad2"
FILES = {
    "__SCENARIOS__": "scenarios.json",
    "__EMOTIONS__":  "emotions.json",
    "__PHRASES__":   "phrases.json",
    "__POLICIES__":  "policies.json",
    "__RUBRIC__":    "rubric.json",
    "__DRILLS__":    "drills.json",
    "__VOCAB__":     "vocab.json",
    "__OPS__":       "ops.json",
}

def anki(action, params):
    req = urllib.request.Request("http://127.0.0.1:8765",
        data=json.dumps({"action": action, "version": 6, "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["result"]

def strip(s): return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()

def vocab_from_anki():
    """Mirror the 'Claude::Inglês Atendimento' deck (tag airbnb) into content/vocab.json."""
    cats = {"encanamento":"Plumbing","eletrodomesticos":"Appliances","moveis":"Furniture","pragas":"Pests",
            "limpeza":"Cleanliness","acesso":"Access","seguranca":"Safety","casa":"Parts of the home",
            "banheiro":"Bathroom","cozinha":"Kitchen","cama":"Bedding","dano":"Damage & condition",
            "processo":"Claims & process","chamada":"On the phone","emergencia":"Emergency & relocation"}
    items = []
    ids = anki("findNotes", {"query": 'tag:airbnb deck:"Claude::Inglês Atendimento::Vocabulário"'})
    for n in anki("notesInfo", {"notes": ids}):
        f, b = n["fields"]["Front"]["value"], n["fields"]["Back"]["value"]
        m = re.search(r"<b>(.*?)</b>", f); pt = strip(m.group(1)) if m else strip(f)
        m = re.match(r"\s*<b>(.*?)</b>", b); en = strip(m.group(1)) if m else ""
        m = re.search(r"<i>(.*?)</i>", b); ex = strip(m.group(1)) if m else ""
        m = re.search(r"<span[^>]*>(.*?)</span>", b); note = strip(m.group(1)) if m else ""
        cat = next((t for t in n["tags"] if t in cats), "outros")
        if en: items.append({"en": en, "pt": pt, "example": ex, "note": note, "cat": cat})
    pairs = []
    pids = anki("findNotes", {"query": 'deck:"Claude::Inglês Atendimento::Britânico x Americano"'})
    for n in anki("notesInfo", {"notes": pids}):
        f, b = n["fields"]["Front"]["value"], n["fields"]["Back"]["value"]
        bs = re.findall(r"<b>(.*?)</b>", f)
        m = re.match(r"\s*<b>(.*?)</b>", b); pt = strip(m.group(1)) if m else ""
        exs = re.findall(r"<span[^>]*>(.*?)</span>", b)
        if len(bs) >= 2:
            pairs.append({"pt": pt, "uk": strip(bs[0]), "us": strip(bs[1]),
                          "example_uk": strip(exs[0]) if exs else "", "example_us": strip(exs[1]) if len(exs) > 1 else ""})
    items.sort(key=lambda x: (x["cat"], x["en"]))
    with open(os.path.join(ROOT, "content", "vocab.json"), "w", encoding="utf-8") as fh:
        json.dump({"_about": "Léxico do app — espelho do baralho Anki (tag airbnb). Regenerar com build.py --vocab-from-anki.",
                   "categories": cats, "items": items, "uk_us_pairs": pairs}, fh, ensure_ascii=False, indent=1)
    print(f"vocab.json refreshed: {len(items)} items, {len(pairs)} pairs")

def build():
    import datetime, shutil
    build_id = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    with open(SRC, encoding="utf-8") as fh: page = fh.read()
    page = page.replace("__BUILD__", build_id).replace("__CLAUDE_URL__", CLAUDE_URL)
    total = 0
    for ph, fn in FILES.items():
        path = os.path.join(ROOT, "content", fn)
        with open(path, encoding="utf-8") as fh: data = json.load(fh)   # validates JSON
        blob = json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")   # ASCII-only: immune to charset issues
        if ph not in page: sys.exit(f"placeholder {ph} missing in index.html")
        page = page.replace(ph, blob); total += len(blob)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh: fh.write(page)
    # PWA site: same page + service worker (stamped) + manifest + icons
    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as fh: fh.write(page)
    with open(os.path.join(ROOT, "sw.js"), encoding="utf-8") as fh: sw = fh.read().replace("__BUILD__", build_id)
    with open(os.path.join(SITE, "sw.js"), "w", encoding="utf-8") as fh: fh.write(sw)
    for fn in ("manifest.webmanifest", "icon-192.png", "icon-512.png"):
        src = os.path.join(ROOT, fn)
        if os.path.exists(src): shutil.copy(src, os.path.join(SITE, fn))
    with open(os.path.join(SITE, ".nojekyll"), "w") as fh: fh.write("")
    print(f"built {OUT} and {SITE}/ (build {build_id}): {len(page):,} chars ({total:,} of content)")

if __name__ == "__main__":
    if "--vocab-from-anki" in sys.argv: vocab_from_anki()
    build()
