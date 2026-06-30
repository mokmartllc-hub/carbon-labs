"""Extract GLP-3 10mg vial PNG from index.html IMGS for OG / product image."""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
text = (ROOT / "public" / "index.html").read_text(encoding="utf-8")

m = re.search(r"glp3_10:\"(data:image/png;base64,[^\"]+)\"", text)
if not m:
    raise SystemExit("glp3_10 image not found in IMGS")

data = base64.b64decode(m.group(1).split(",", 1)[1])
img_dir = ROOT / "public" / "images"
img_dir.mkdir(exist_ok=True)

for name, dest in (
    ("glp3-10mg.png", img_dir / "glp3-10mg.png"),
    ("og-image.png", ROOT / "public" / "og-image.png"),
):
    dest.write_bytes(data)
    print(f"wrote {dest.relative_to(ROOT)} ({len(data)} bytes)")
