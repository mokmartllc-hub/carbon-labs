from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")
old = '</script>\n<script src="/api.js"></script>\n</body></html>'
new = (
    '</script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>\n'
    '<script src="/config.js"></script>\n'
    '<script src="/api.js"></script>\n'
    '</body></html>'
)
if old not in text:
    raise SystemExit("pattern not found")
p.write_text(text.replace(old, new, 1), encoding="utf-8")
print("patched supabase scripts")
