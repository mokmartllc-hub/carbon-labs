"""Add Open Graph / Twitter meta tags for rich link previews (iMessage, etc.)."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

OLD_HEAD = (
    '<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    "<title>Carbon Labs</title>"
)

OG = """<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Carbon Labs — Research-Grade Peptides</title>
<meta name="description" content="Premium research-grade peptides. Third-party tested, 99%+ purity. Free shipping · Ships in 24–48 hours · NY, USA.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Carbon Labs">
<meta property="og:title" content="Carbon Labs — Research-Grade Peptides">
<meta property="og:description" content="Premium research-grade peptides. Third-party tested, 99%+ purity. Free shipping on every order.">
<meta property="og:url" content="https://carbon-labs.vercel.app/">
<meta property="og:image" content="https://carbon-labs.vercel.app/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Carbon Labs — Research-Grade Peptides">
<meta name="twitter:description" content="Premium research-grade peptides. Third-party tested, 99%+ purity. Free shipping on every order.">
<meta name="twitter:image" content="https://carbon-labs.vercel.app/og-image.png">"""

if "og:image" in text.split("</head>")[0]:
    print("og tags already present")
elif OLD_HEAD in text:
    text = text.replace(OLD_HEAD, OG, 1)
    p.write_text(text, encoding="utf-8")
    print("og tags added")
else:
    raise SystemExit("head block not found")
