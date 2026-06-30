"""Move hamburger left of logo on mobile; show Login / Sign Up on mobile nav."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

BURGER_BTN = (
    '<button type="button" class="navburger" onclick="openNav()" aria-label="Open menu">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">'
    '<path d="M4 7h16M4 12h16M4 17h16"/></svg></button>'
)

OLD_NR = (
    '<div class="nr"><button type="button" class="navburger" onclick="openNav()" aria-label="Open menu">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">'
    '<path d="M4 7h16M4 12h16M4 17h16"/></svg></button><span class="nlog" id="navauth"'
)
NEW_NR = '<div class="nr"><span class="nlog" id="navauth"'

if OLD_NR in text:
    text = text.replace(OLD_NR, NEW_NR, 1)

OLD_NAV_START = '  <nav>\n    <div class="wm wm-sm"'
if OLD_NAV_START in text and BURGER_BTN not in text.split('<div class="wm wm-sm"')[0][-400:]:
    text = text.replace(OLD_NAV_START, f"  <nav>\n    {BURGER_BTN}\n    <div class=\"wm wm-sm\"", 1)

text = text.replace(
    '<span class="nlog-short">Login</span>',
    '<span class="nlog-short">Login / Sign Up</span>',
)

text = text.replace(
    "nav>.wm,nav>.nr{position:relative;z-index:1;flex-shrink:0}",
    "nav>.wm,nav>.nr,nav>.navburger{position:relative;z-index:1;flex-shrink:0}",
    1,
)

OLD_MOBILE_NAV = """  nav{display:flex;flex-wrap:nowrap;align-items:center;height:56px;min-height:56px;padding:0 14px;gap:8px}
  nav>.nl{display:none!important}
  nav>.wm{flex:0 1 auto;min-width:0}
  nav .nr{margin-left:auto;gap:8px;flex-shrink:0;align-items:center}
  .navburger{display:flex}"""

NEW_MOBILE_NAV = """  nav{display:flex;flex-wrap:nowrap;align-items:center;height:56px;min-height:56px;padding:0 14px;gap:10px}
  nav>.nl{display:none!important}
  nav>.navburger{display:flex;order:0;margin-right:2px}
  nav>.wm{flex:0 1 auto;min-width:0;order:1}
  nav .nr{margin-left:auto;gap:8px;flex-shrink:0;align-items:center;order:2}
  .navburger{display:flex}"""

if OLD_MOBILE_NAV in text:
    text = text.replace(OLD_MOBILE_NAV, NEW_MOBILE_NAV, 1)
elif "nav>.navburger{display:flex;order:0" in text:
    print("mobile nav css ok")
else:
    raise SystemExit("mobile nav CSS block not found")

if BURGER_BTN not in text.split('<div class="wm wm-sm"')[0]:
    raise SystemExit("burger not before logo")
if 'nlog-short">Login / Sign Up' not in text:
    raise SystemExit("login label not updated")

p.write_text(text, encoding="utf-8")
print("mobile nav layout patched")
