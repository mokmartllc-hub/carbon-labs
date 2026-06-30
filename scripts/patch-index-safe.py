"""Patch index.html safely via Python (never use editor replace on huge file)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"

if len(sys.argv) < 2:
    raise SystemExit("usage: patch-index-safe.py <patch-name>")

name = sys.argv[1]
text = p.read_text(encoding="utf-8")
before = len(text)

if name == "og-dimensions":
    text = text.replace(
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:width" content="1122">',
        1,
    )
    text = text.replace(
        '<meta property="og:image:height" content="1200">',
        '<meta property="og:image:height" content="1402">',
        1,
    )
else:
    raise SystemExit(f"unknown patch: {name}")

if len(text) < 10_000_000 or not text.rstrip().endswith("</html>"):
    raise SystemExit(f"REFUSING TO WRITE: file looks truncated ({len(text)} bytes)")

p.write_text(text, encoding="utf-8")
print(f"patched {name}: {before} -> {len(text)} bytes")
