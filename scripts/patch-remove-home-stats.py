"""Remove 100K+ orders shipped and 5 quality checks from home and about pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"
text = p.read_text(encoding="utf-8")
before = len(text)

REMOVALS = [
    '\n        <div class="hst"><div class="v">100K+</div><div class="l">Orders Shipped</div></div>',
    '\n      <div class="qitem"><div class="qval">5</div><div class="qlbl">Quality Checks</div></div>',
    """          <div class="about-stat-card">
            <div class="asc-val">100K+</div>
            <div class="asc-lbl">Orders Shipped</div>
            <div class="asc-sub">Trusted by researchers nationwide</div>
          </div>""",
    """          <div class="about-stat-card">
            <div class="asc-val">5</div>
            <div class="asc-lbl">Quality Checks</div>
            <div class="asc-sub">From synthesis to delivery</div>
          </div>""",
]

for block in REMOVALS:
    count = text.count(block)
    if count == 0:
        print(f"already gone: {block.strip()[:50]}")
    elif count == 1:
        text = text.replace(block, "", 1)
        print(f"removed: {block.strip()[:50]}")
    else:
        raise SystemExit(f"ambiguous block ({count} matches): {block.strip()[:50]}")

if len(text) < 10_000_000 or not text.rstrip().endswith("</html>"):
    raise SystemExit(f"REFUSING TO WRITE: truncated ({len(text)} bytes)")

p.write_text(text, encoding="utf-8")
print(f"Done: {before} -> {len(text)} bytes")
