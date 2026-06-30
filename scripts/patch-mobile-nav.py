"""Fix mobile nav and about page layout in index.html."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")
patches = []

MOBILE_CSS = """
/* ===== MOBILE LAYOUT ===== */
.nlog-short{display:none}
.nca-cart-word{display:inline}
@media(max-width:768px){
  nav{flex-wrap:wrap;align-items:center;height:auto;min-height:56px;padding:10px 14px;gap:8px}
  nav>.wm{order:1;flex:0 1 auto;min-width:0}
  nav .nr{order:2;margin-left:auto;gap:8px;flex-shrink:0;align-items:center}
  nav .nl{order:3;width:100%;flex:1 1 100%;display:flex;gap:18px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:10px 0 2px;border-top:1px solid rgba(255,255,255,.06);margin-top:2px}
  nav .nl::-webkit-scrollbar{display:none}
  nav .nl a{white-space:nowrap;flex-shrink:0;font-size:12px}
  .nlog{font-size:12px;white-space:nowrap;line-height:1}
  .nlog-full{display:none}
  .nlog-short{display:inline}
  .nca{padding:8px 10px;font-size:12px;gap:5px;flex-shrink:0}
  .nca-cart-word{display:none}
  .user-pill-name,.user-caret{display:none!important}
  .user-pill .ua{width:32px;height:32px;font-size:12px}
  .about-sec{padding:48px 20px}
  .about-two-col{grid-template-columns:1fr;gap:32px;max-width:100%}
  .about-stats-col{width:100%}
  .about-vals{grid-template-columns:1fr;gap:14px}
  .about-sec-inner{max-width:100%}
  .pg-hero{padding:72px 20px 48px}
  .pg-title{font-size:32px}
  .pg-sub{font-size:14px}
  .about-cta-band{padding:48px 20px}
  .about-cta-band h2{font-size:24px}
  .tl-item{gap:16px;margin-bottom:28px}
  .tl-num{flex-shrink:0;width:36px;height:36px;font-size:12px}
  .hero{padding:56px 20px 48px}
  .hero h1{font-size:34px}
  .hstats{flex-direction:column;width:100%;max-width:340px}
  .hst{border-right:none;border-bottom:1px solid rgba(255,255,255,.07)}
  .hst:last-child{border-bottom:none}
  .sec{padding:48px 20px}
  .sh h2{font-size:24px}
  .pgrid{grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}
  .cartdr{width:100%;max-width:100%}
}
@media(max-width:480px){
  nav .nl{gap:14px}
  .nca{padding:8px 9px}
  .about-stat-card{padding:18px 20px}
  .aval{padding:20px}
}
"""

if "/* ===== MOBILE LAYOUT ===== */" not in text:
    text = text.replace(
        "@media(max-width:768px){.acct-layout{grid-template-columns:1fr}",
        MOBILE_CSS + "@media(max-width:768px){.acct-layout{grid-template-columns:1fr}",
        1,
    )
    patches.append("css")

OLD_NAV_AUTH = '<span class="nlog" id="navauth" onclick="go(\'auth\')">Login / Sign Up</span>'
NEW_NAV_AUTH = '<span class="nlog" id="navauth" onclick="go(\'auth\')"><span class="nlog-full">Login / Sign Up</span><span class="nlog-short">Login</span></span>'
if OLD_NAV_AUTH in text:
    text = text.replace(OLD_NAV_AUTH, NEW_NAV_AUTH, 1)
    patches.append("nav-auth")

OLD_CART = (
    '<button class="nca" onclick="openCart()"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">'
    '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>'
    '<path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>'
    'Cart (<span id="cc">0</span>)</button>'
)
NEW_CART = (
    '<button class="nca" onclick="openCart()" aria-label="Open cart"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">'
    '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>'
    '<path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>'
    '<span class="nca-full"><span class="nca-cart-word">Cart </span>(<span id="cc">0</span>)</span></button>'
)
if 'class="nca-full"' not in text and 'Cart (<span id="cc">' in text:
    text = text.replace(
        '<button class="nca" onclick="openCart()"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>Cart (<span id="cc">0</span>)</button>',
        NEW_CART,
        1,
    )
    patches.append("cart-btn")

OLD_USER_MENU = (
    'target.outerHTML=`<div class="user-menu" id="user-menu"><div class="user-pill" onclick="toggleUserMenu()">'
    '<div class="ua">${ini}</div><span style="font-size:13px;color:rgba(255,255,255,.75);font-weight:600">${currentUser.first}</span>'
    '<span style="font-size:10px;color:rgba(255,255,255,.35);margin-left:2px">▾</span></div>'
)
NEW_USER_MENU = (
    'target.outerHTML=`<div class="user-menu" id="user-menu"><div class="user-pill" onclick="toggleUserMenu()">'
    '<div class="ua">${ini}</div><span class="user-pill-name" style="font-size:13px;color:rgba(255,255,255,.75);font-weight:600">${currentUser.first}</span>'
    '<span class="user-caret" style="font-size:10px;color:rgba(255,255,255,.35);margin-left:2px">▾</span></div>'
)
if 'user-pill-name' not in text and OLD_USER_MENU.split('${ini}')[0] in text:
    text = text.replace(OLD_USER_MENU, NEW_USER_MENU, 1)
    patches.append("user-menu")

OLD_SIGNOUT_NAV = (
    'if(existing)existing.outerHTML=`<span class="nlog" id="navauth" onclick="go(\'auth\')">Login / Sign Up</span>`;'
)
NEW_SIGNOUT_NAV = (
    'if(existing)existing.outerHTML=`<span class="nlog" id="navauth" onclick="go(\'auth\')">'
    '<span class="nlog-full">Login / Sign Up</span><span class="nlog-short">Login</span></span>`;'
)
if OLD_SIGNOUT_NAV in text:
    text = text.replace(OLD_SIGNOUT_NAV, NEW_SIGNOUT_NAV, 1)
    patches.append("signout-nav")

USER_OLD = (
    '<span style="font-size:13px;color:rgba(255,255,255,.75);font-weight:600">${currentUser.first}</span>'
    '<span style="font-size:10px;color:rgba(255,255,255,.35);margin-left:2px">\u25be</span>'
)
USER_NEW = (
    '<span class="user-pill-name" style="font-size:13px;color:rgba(255,255,255,.75);font-weight:600">${currentUser.first}</span>'
    '<span class="user-caret" style="font-size:10px;color:rgba(255,255,255,.35);margin-left:2px">\u25be</span>'
)
if 'class="user-pill-name"' not in text and USER_OLD in text:
    text = text.replace(USER_OLD, USER_NEW, 1)
    patches.append("user-menu")

p.write_text(text, encoding="utf-8")
print("patched:", ", ".join(patches) or "nothing needed")
print("size", p.stat().st_size)
