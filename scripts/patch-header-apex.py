"""Apex-style header: viewport-centered nav links + static announcement bar."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

# --- Ticker: static 3-column layout ---
OLD_TICKER_CSS = """/* TICKER */
.tk{background:rgba(255,255,255,.03);border-bottom:1px solid rgba(255,255,255,.05);color:rgba(255,255,255,.5);font-size:11px;letter-spacing:.07em;overflow:hidden;padding:8px 0;white-space:nowrap;position:relative;z-index:10}
.tkt{display:inline-flex;animation:tkk 36s linear infinite;white-space:nowrap}
.tkt span{margin:0 36px}
@keyframes tkk{from{transform:translateX(0)}to{transform:translateX(-50%)}}"""

NEW_TICKER_CSS = """/* TICKER */
.tk{background:rgba(255,255,255,.03);border-bottom:1px solid rgba(255,255,255,.05);color:rgba(255,255,255,.5);font-size:11px;letter-spacing:.06em;position:relative;z-index:10;padding:9px 36px}
.tk-inner{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:16px;max-width:100%}
.tk-left{justify-self:start;white-space:nowrap}
.tk-center{justify-self:center;display:flex;align-items:center;gap:14px;white-space:nowrap}
.tk-right{justify-self:end;white-space:nowrap;text-align:right}
.tk-dot{opacity:.35}"""

OLD_NAV = (
    "nav{background:rgba(12,12,12,.55);backdrop-filter:blur(20px) saturate(120%);"
    "border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;"
    "justify-content:space-between;padding:0 36px;height:64px;position:sticky;top:0;z-index:100}"
    "nav>.nl{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:0}"
    "nav>.wm,nav>.nr{position:relative;z-index:1}"
)
NEW_NAV = (
    "nav{background:rgba(12,12,12,.55);backdrop-filter:blur(20px) saturate(120%);"
    "border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;"
    "justify-content:space-between;padding:0 36px;height:64px;position:sticky;top:0;z-index:100}"
    "nav>.nl{position:absolute;left:0;right:0;display:flex;justify-content:center;align-items:center;"
    "gap:32px;pointer-events:none;z-index:0}"
    "nav>.nl a{pointer-events:auto}"
    "nav>.wm,nav>.nr{position:relative;z-index:1;flex-shrink:0}"
)

OLD_TICKER_HTML = """  <div class="tk"><div class="tkt">
    <span>Free Shipping On All Orders</span><span>·</span><span>Ships in 24–48 Business Hours</span><span>·</span><span>Third-Party Tested · 99%+ Purity</span><span>·</span><span>Buy 3 Get 1 · Buy 6 Get 2 · Buy 10 Get 4 · Buy 2 Get Free Bac Water</span><span>·</span>
    <span>Free Shipping On All Orders</span><span>·</span><span>Ships in 24–48 Business Hours</span><span>·</span><span>Third-Party Tested · 99%+ Purity</span><span>·</span><span>Buy 3 Get 1 · Buy 6 Get 2 · Buy 10 Get 4 · Buy 2 Get Free Bac Water</span><span>·</span>
  </div></div>"""

NEW_TICKER_HTML = """  <div class="tk"><div class="tk-inner">
    <div class="tk-left">Buy 2 Get Free Bac Water</div>
    <div class="tk-center"><span>Free Shipping On All Orders</span><span class="tk-dot">·</span><span>Ships in 24–48 Business Hours</span><span class="tk-dot">·</span><span>Third-Party Tested · 99%+ Purity</span></div>
    <div class="tk-right">Buy 3 Get 1 · Buy 6 Get 2 · Buy 10 Get 4</div>
  </div></div>"""

# Slightly wider link spacing like reference
text = text.replace(".nl{display:flex;gap:28px}", ".nl{display:flex;gap:32px}", 1)

if OLD_TICKER_CSS in text:
    text = text.replace(OLD_TICKER_CSS, NEW_TICKER_CSS, 1)
    print("ticker css")
elif ".tk-inner{" in text:
    print("ticker css ok")

if OLD_NAV in text:
    text = text.replace(OLD_NAV, NEW_NAV, 1)
    print("nav css")
elif "nav>.nl{position:absolute;left:0;right:0" in text:
    print("nav css ok")
else:
    raise SystemExit("nav css not found")

if OLD_TICKER_HTML in text:
    text = text.replace(OLD_TICKER_HTML, NEW_TICKER_HTML, 1)
    print("ticker html")
elif 'class="tk-inner"' in text:
    print("ticker html ok")
else:
    raise SystemExit("ticker html not found")

# Mobile: hide static ticker sides, show compact center only
OLD_MOBILE_START = "@media(max-width:768px){\n  nav{display:flex;"
MOBILE_TICKER = """@media(max-width:768px){
  .tk{padding:8px 14px}
  .tk-inner{grid-template-columns:1fr;justify-items:center;text-align:center}
  .tk-left,.tk-right{display:none}
  .tk-center{flex-wrap:wrap;justify-content:center;gap:8px 12px;font-size:10px}
  nav{display:flex;"""

if OLD_MOBILE_START in text and ".tk-left,.tk-right{display:none}" not in text:
    text = text.replace(OLD_MOBILE_START, MOBILE_TICKER, 1)
    print("mobile ticker")

p.write_text(text, encoding="utf-8")
print("done")
