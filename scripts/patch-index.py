"""Safely patch public/index.html — use Python to avoid truncating large files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"
text = p.read_text(encoding="utf-8")

ACCOUNT_CSS = """
/* account + orders */
.acct-wrap{max-width:980px;margin:0 auto;padding:48px 36px 80px}
.acct-layout{display:grid;grid-template-columns:220px 1fr;gap:32px;align-items:start}
.acct-nav{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:12px;position:sticky;top:88px}
.acct-nav a{display:block;padding:10px 14px;font-size:13px;font-weight:600;color:rgba(255,255,255,.5);border-radius:8px;cursor:pointer;text-decoration:none;margin-bottom:2px}
.acct-nav a:hover,.acct-nav a.active{background:rgba(255,255,255,.08);color:white}
.acct-card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:28px 32px;backdrop-filter:blur(8px)}
.acct-card h2{font-size:18px;font-weight:800;color:white;margin-bottom:6px}
.acct-card .acct-sub{font-size:13px;color:rgba(255,255,255,.38);margin-bottom:24px;line-height:1.6}
.acct-row{display:flex;gap:16px;margin-bottom:16px}
.acct-row .auth-field{flex:1;margin-bottom:0}
.acct-email-note{font-size:12px;color:rgba(255,255,255,.35);margin-top:-8px;margin-bottom:20px}
.acct-saved{font-size:12px;color:var(--a2);margin-top:12px;display:none}
.acct-saved.show{display:block}
.orders-list{display:flex;flex-direction:column;gap:12px}
.order-card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:12px;overflow:hidden;transition:border-color .2s}
.order-card.open{border-color:rgba(255,255,255,.2)}
.order-hd{display:flex;justify-content:space-between;align-items:center;padding:18px 22px;cursor:pointer;gap:16px;flex-wrap:wrap}
.order-hd:hover{background:rgba(255,255,255,.03)}
.order-num{font-size:14px;font-weight:800;color:white}
.order-meta{font-size:12px;color:rgba(255,255,255,.4);margin-top:3px}
.order-hd-right{text-align:right}
.order-total{font-size:16px;font-weight:800;color:var(--a2)}
.order-status{display:inline-block;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;padding:4px 10px;border-radius:20px;margin-top:4px}
.order-status.confirmed{background:rgba(100,100,100,.2);color:#ccc}
.order-status.processing{background:rgba(200,180,80,.15);color:#e8d080}
.order-status.shipped{background:rgba(80,140,200,.15);color:#80b8e8}
.order-status.delivered{background:rgba(80,180,120,.15);color:#80d8a0}
.order-bd{display:none;padding:0 22px 22px;border-top:1px solid rgba(255,255,255,.07)}
.order-card.open .order-bd{display:block}
.order-items{margin:16px 0}
.order-item{display:flex;justify-content:space-between;padding:8px 0;font-size:13px;color:rgba(255,255,255,.65);border-bottom:1px solid rgba(255,255,255,.05)}
.order-item:last-child{border-bottom:none}
.order-ship{font-size:12px;color:rgba(255,255,255,.4);line-height:1.7;margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,.07)}
.orders-empty{text-align:center;padding:60px 24px;color:rgba(255,255,255,.4)}
.orders-empty h3{font-size:18px;font-weight:800;color:white;margin-bottom:8px}
.orders-loading{text-align:center;padding:48px;color:rgba(255,255,255,.4);font-size:13px}
@media(max-width:768px){.acct-layout{grid-template-columns:1fr}.acct-nav{position:static;display:flex;gap:4px;overflow-x:auto}.acct-nav a{white-space:nowrap}}
"""

ACCOUNT_PAGES = """
  <!-- ===== MY ACCOUNT ===== -->
  <div id="paccount" class="page">
    <div class="pg-hero" style="padding:72px 36px 48px">
      <div class="pg-hero-inner">
        <div class="pg-eyebrow">Your Account</div>
        <h1 class="pg-title">My <span class="hl">Account</span></h1>
        <p class="pg-sub">Manage your profile, password, and account settings.</p>
      </div>
    </div>
    <div class="acct-wrap"><div id="account-root"></div></div>
    <div class="pg-footer-mini"></div>
  </div>

  <!-- ===== ORDER HISTORY ===== -->
  <div id="porders" class="page">
    <div class="pg-hero" style="padding:72px 36px 48px">
      <div class="pg-hero-inner">
        <div class="pg-eyebrow">Your Orders</div>
        <h1 class="pg-title">Order <span class="hl">History</span></h1>
        <p class="pg-sub">View past orders, shipping details, and order status.</p>
      </div>
    </div>
    <div class="acct-wrap"><div id="orders-root"></div></div>
    <div class="pg-footer-mini"></div>
  </div>
"""

patches = []

if "/* account + orders */" not in text:
    text = text.replace("</style>", ACCOUNT_CSS + "</style>", 1)
    patches.append("css")

marker = '    <div class="pg-footer-mini"></div>\n  </div>\n\n</div>\n\n<div class="cartov"'
if "id=\"paccount\"" not in text and marker in text:
    text = text.replace(
        marker,
        '    <div class="pg-footer-mini"></div>\n  </div>\n' + ACCOUNT_PAGES + "\n</div>\n\n<div class=\"cartov\"",
        1,
    )
    patches.append("pages")

old_go = "['home','shop','prod','about','coa','contact','auth'].forEach"
new_go = "['home','shop','prod','about','coa','contact','auth','account','orders'].forEach"
if old_go in text:
    text = text.replace(old_go, new_go, 1)
    patches.append("go-list")

old_go2 = "document.getElementById('p'+pg).classList.add('active');"
new_go2 = "const pgEl=document.getElementById('p'+pg);if(pgEl)pgEl.classList.add('active');"
if old_go2 in text and new_go2 not in text:
    text = text.replace(old_go2, new_go2, 1)
    patches.append("go-null-safe")

old_nav = '<a>My Account</a><a>Order History</a>'
new_nav = '<a onclick="go(\'account\')">My Account</a><a onclick="go(\'orders\')">Order History</a>'
if old_nav in text:
    text = text.replace(old_nav, new_nav, 1)
    patches.append("nav-links")

scripts = (
    '\n<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
    '\n<script src="/config.js"></script>'
    '\n<script src="/api.js"></script>'
)
if "/api.js" not in text:
    text = text.replace("</body></html>", scripts + "\n</body></html>", 1)
    patches.append("scripts")

p.write_text(text, encoding="utf-8")
print("patched:", ", ".join(patches) or "nothing needed")
print("size", p.stat().st_size, "bytes")
