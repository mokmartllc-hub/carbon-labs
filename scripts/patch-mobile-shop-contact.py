"""Fix mobile shop grid (2 columns) and contact page layout."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

SHOP_CONTACT_CSS = """
  .pgrid,.sgrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
  .sbody{padding:18px 14px 32px}
  .shero{padding:28px 20px 18px}
  .shero h1{font-size:22px}
  .shero p{font-size:12px;line-height:1.55}
  .sbar{padding:10px 14px;gap:8px;top:100px}
  .scats{padding:8px 14px;gap:6px}
  .sinput{min-width:0}
  .pimg{height:190px}
  .pbody{padding:11px 12px 13px}
  .pbody h3{font-size:12px;line-height:1.3}
  .pcat{font-size:10px;line-height:1.35;margin-bottom:6px}
  .pfoot{gap:6px;flex-wrap:wrap}
  .pprice{font-size:12px}
  .badd{padding:6px 9px;font-size:10px;white-space:nowrap}
  .qtystep-sm .qtybtn{width:24px;height:24px;font-size:14px}
  .qtystep-sm .qtyval{font-size:11px;min-width:16px}
  .contact-sec{padding:28px 16px 56px;overflow-x:hidden}
  .contact-inner{grid-template-columns:1fr;gap:28px;max-width:100%}
  .contact-left,.contact-right{min-width:0;max-width:100%}
  .contact-form-card{position:static;top:auto;padding:24px 18px}
  .contact-faqs .sh{margin-top:28px!important}
  .cc-item{padding:16px 0;gap:12px}
  .cc-value{font-size:14px;word-break:break-word}
  .cfaq-q{font-size:12px;gap:10px}
"""

MARKER = "  .pgrid{grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}\n  .cartdr{width:100%;max-width:100%}"
REPLACEMENT = (
    "  .pgrid,.sgrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}\n"
    "  .sbody{padding:18px 14px 32px}\n"
    "  .shero{padding:28px 20px 18px}\n"
    "  .shero h1{font-size:22px}\n"
    "  .shero p{font-size:12px;line-height:1.55}\n"
    "  .sbar{padding:10px 14px;gap:8px;top:100px}\n"
    "  .scats{padding:8px 14px;gap:6px}\n"
    "  .sinput{min-width:0}\n"
    "  .pimg{height:190px}\n"
    "  .pbody{padding:11px 12px 13px}\n"
    "  .pbody h3{font-size:12px;line-height:1.3}\n"
    "  .pcat{font-size:10px;line-height:1.35;margin-bottom:6px}\n"
    "  .pfoot{gap:6px;flex-wrap:wrap}\n"
    "  .pprice{font-size:12px}\n"
    "  .badd{padding:6px 9px;font-size:10px;white-space:nowrap}\n"
    "  .qtystep-sm .qtybtn{width:24px;height:24px;font-size:14px}\n"
    "  .qtystep-sm .qtyval{font-size:11px;min-width:16px}\n"
    "  .contact-sec{padding:28px 16px 56px;overflow-x:hidden}\n"
    "  .contact-inner{grid-template-columns:1fr;gap:28px;max-width:100%}\n"
    "  .contact-left,.contact-right{min-width:0;max-width:100%}\n"
    "  .contact-form-card{position:static;top:auto;padding:24px 18px}\n"
    "  .contact-faqs .sh{margin-top:28px!important}\n"
    "  .cc-item{padding:16px 0;gap:12px}\n"
    "  .cc-value{font-size:14px;word-break:break-word}\n"
    "  .cfaq-q{font-size:12px;gap:10px}\n"
    "  .cartdr{width:100%;max-width:100%}"
)

patches = []
if MARKER in text:
    text = text.replace(MARKER, REPLACEMENT, 1)
    patches.append("mobile-shop-contact")
elif ".sgrid{grid-template-columns:repeat(2" in text:
    patches.append("already-patched")
else:
    patches.append("marker-not-found")

p.write_text(text, encoding="utf-8")
print("patched:", ", ".join(patches))
print("size", p.stat().st_size)
