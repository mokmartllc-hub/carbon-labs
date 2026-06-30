"""Add favicon link tags to index.html."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

links = (
    '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
    '<link rel="icon" href="/favicon.png" type="image/png" sizes="32x32">'
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png">'
)

if 'href="/favicon.svg"' in text:
    print("favicon links already present")
else:
    text = text.replace("<title>Carbon Labs</title>", f"<title>Carbon Labs</title>{links}", 1)
    p.write_text(text, encoding="utf-8")
    print("added favicon links")
