"""Remove Phone / Text channel from contact page."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

old = """            <div class="cc-item">
              <div class="cc-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg></div>
              <div>
                <div class="cc-label">Phone / Text</div>
                <div class="cc-value">+1 (929) 000-0000</div>
                <div class="cc-note">Call or text — available 24/7</div>
              </div>
            </div>
"""

if old not in text:
    raise SystemExit("Phone / Text block not found (already removed?)")

p.write_text(text.replace(old, "", 1), encoding="utf-8")
print("Removed Phone / Text from contact page.")
