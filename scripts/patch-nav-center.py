"""True viewport-centered nav links via absolute positioning."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

OLD_NAV = (
    "nav{background:rgba(12,12,12,.55);backdrop-filter:blur(20px) saturate(120%);"
    "border-bottom:1px solid rgba(255,255,255,.06);display:grid;grid-template-columns:1fr auto 1fr;"
    "align-items:center;padding:0 36px;height:64px;position:sticky;top:0;z-index:100}"
    "nav>.wm{justify-self:start}nav>.nl{justify-self:center}nav>.nr{justify-self:end}"
)
NEW_NAV = (
    "nav{background:rgba(12,12,12,.55);backdrop-filter:blur(20px) saturate(120%);"
    "border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;"
    "justify-content:space-between;padding:0 36px;height:64px;position:sticky;top:0;z-index:100}"
    "nav>.nl{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:0}"
    "nav>.wm,nav>.nr{position:relative;z-index:1}"
)

OLD_MOBILE_NL = (
    "  nav .nl{order:3;width:100%;flex:1 1 100%;display:flex;gap:18px;"
)
NEW_MOBILE_NL = (
    "  nav .nl{order:3;position:static;left:auto;top:auto;transform:none;z-index:auto;"
    "width:100%;flex:1 1 100%;display:flex;gap:18px;"
)

if OLD_NAV in text:
    text = text.replace(OLD_NAV, NEW_NAV, 1)
    print("desktop nav: absolute center")
elif "nav>.nl{position:absolute;left:50%" in text:
    print("desktop nav already patched")
else:
    raise SystemExit("desktop nav CSS not found")

if OLD_MOBILE_NL in text:
    text = text.replace(OLD_MOBILE_NL, NEW_MOBILE_NL, 1)
    print("mobile nav: reset absolute positioning")
elif "position:static;left:auto;top:auto;transform:none" in text:
    print("mobile nav already patched")
else:
    raise SystemExit("mobile nav CSS not found")

p.write_text(text, encoding="utf-8")
print("done")
