"""Mobile hamburger menu with slide-out nav drawer."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

# --- CSS ---
NAV_DRAWER_CSS = """
.navburger{display:none;align-items:center;justify-content:center;width:40px;height:40px;padding:0;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:9px;cursor:pointer;color:rgba(255,255,255,.75);flex-shrink:0}
.navburger svg{width:18px;height:18px}
.navov{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:290;backdrop-filter:blur(4px)}
.navov.open{display:block}
.navdr{position:fixed;left:0;top:0;bottom:0;width:min(300px,86vw);background:#111111;border-right:1px solid rgba(255,255,255,.08);display:flex;flex-direction:column;z-index:291;transform:translateX(-100%);transition:transform .3s cubic-bezier(.4,0,.2,1)}
.navdr.open{transform:translateX(0)}
.navdr-hd{display:flex;justify-content:space-between;align-items:center;padding:18px 20px;border-bottom:1px solid rgba(255,255,255,.08)}
.navdr-hd span{font-size:14px;font-weight:800;color:white;letter-spacing:.04em}
.navdr-close{background:none;border:none;font-size:24px;line-height:1;cursor:pointer;color:rgba(255,255,255,.35);padding:4px}
.navdr-links{display:flex;flex-direction:column;padding:12px 10px;gap:4px}
.navdr-links a{display:block;padding:14px 16px;font-size:15px;font-weight:600;color:rgba(255,255,255,.55);text-decoration:none;border-radius:10px;cursor:pointer;transition:background .15s,color .15s}
.navdr-links a:hover{background:rgba(255,255,255,.06);color:rgba(255,255,255,.85)}
.navdr-links a.active{background:rgba(255,255,255,.08);color:white}
"""

if ".navburger{" not in text:
    text = text.replace(
        ".nca:hover{background:#444444;color:white}",
        ".nca:hover{background:#444444;color:white}" + NAV_DRAWER_CSS,
        1,
    )

OLD_MOBILE_NAV = """@media(max-width:768px){
  nav{display:flex;flex-wrap:wrap;align-items:center;height:auto;min-height:56px;padding:10px 14px;gap:8px}
  nav>.wm{order:1;flex:0 1 auto;min-width:0}
  nav .nr{order:2;margin-left:auto;gap:8px;flex-shrink:0;align-items:center}
  nav .nl{order:3;position:static;left:auto;top:auto;transform:none;z-index:auto;width:100%;flex:1 1 100%;display:flex;gap:18px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:10px 0 2px;border-top:1px solid rgba(255,255,255,.06);margin-top:2px}
  nav .nl::-webkit-scrollbar{display:none}
  nav .nl a{white-space:nowrap;flex-shrink:0;font-size:12px}"""

NEW_MOBILE_NAV = """@media(max-width:768px){
  nav{display:flex;flex-wrap:nowrap;align-items:center;height:56px;min-height:56px;padding:0 14px;gap:8px}
  nav>.nl{display:none!important}
  nav>.wm{flex:0 1 auto;min-width:0}
  nav .nr{margin-left:auto;gap:8px;flex-shrink:0;align-items:center}
  .navburger{display:flex}"""

if OLD_MOBILE_NAV in text:
    text = text.replace(OLD_MOBILE_NAV, NEW_MOBILE_NAV, 1)
elif "nav>.nl{display:none!important}" in text:
    pass
else:
    raise SystemExit("mobile nav block not found")

# shop sticky bar was offset for 2-row nav
text = text.replace(
    "  .sbar{padding:10px 14px;gap:8px;top:100px}",
    "  .sbar{padding:10px 14px;gap:8px;top:56px}",
    1,
)

# --- HTML: data-nav on desktop links + hamburger button ---
OLD_NL = '<div class="nl"><a onclick="go(\'home\')" id="nh" class="active">Home</a><a onclick="go(\'shop\')" id="ns">Shop</a><a onclick="go(\'about\')" id="na">About</a><a onclick="go(\'coa\')" id="nc">COA</a><a onclick="go(\'contact\')" id="nct">Contact</a></div>'
NEW_NL = '<div class="nl"><a data-nav="home" onclick="go(\'home\')" id="nh" class="active">Home</a><a data-nav="shop" onclick="go(\'shop\')" id="ns">Shop</a><a data-nav="about" onclick="go(\'about\')" id="na">About</a><a data-nav="coa" onclick="go(\'coa\')" id="nc">COA</a><a data-nav="contact" onclick="go(\'contact\')" id="nct">Contact</a></div>'

OLD_NR = '<div class="nr"><span class="nlog" id="navauth"'
NEW_NR = (
    '<div class="nr">'
    '<button type="button" class="navburger" onclick="openNav()" aria-label="Open menu">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">'
    '<path d="M4 7h16M4 12h16M4 17h16"/></svg></button>'
    '<span class="nlog" id="navauth"'
)

if OLD_NL in text and 'data-nav="home"' not in text:
    text = text.replace(OLD_NL, NEW_NL, 1)

if '<button type="button" class="navburger"' not in text and OLD_NR in text:
    text = text.replace(OLD_NR, NEW_NR, 1)

# Drawer after </nav>
NAV_DRAWER_HTML = """
<div class="navov" id="navov" onclick="closeNav()"></div>
<div class="navdr" id="navdr">
  <div class="navdr-hd"><span>Menu</span><button type="button" class="navdr-close" onclick="closeNav()" aria-label="Close menu">×</button></div>
  <div class="navdr-links">
    <a data-nav="home" onclick="navGo('home')">Home</a>
    <a data-nav="shop" onclick="navGo('shop')">Shop</a>
    <a data-nav="about" onclick="navGo('about')">About</a>
    <a data-nav="coa" onclick="navGo('coa')">COA</a>
    <a data-nav="contact" onclick="navGo('contact')">Contact</a>
  </div>
</div>
"""

if 'id="navdr"' not in text:
    text = text.replace(
        "  </nav>\n\n  <div id=\"phome\"",
        "  </nav>" + NAV_DRAWER_HTML + "\n  <div id=\"phome\"",
        1,
    )

# --- JS ---
OLD_GO = """function go(pg){
  ['home','shop','prod','about','coa','contact','auth','account','orders','admin'].forEach(id=>{const el=document.getElementById('p'+id);if(el)el.classList.remove('active');});
  const pgEl=document.getElementById('p'+pg);if(pgEl)pgEl.classList.add('active');
  ['nh','ns','na','nc','nct'].forEach(id=>{const el=document.getElementById(id);if(el)el.classList.remove('active');});
  const navMap={home:'nh',shop:'ns',about:'na',coa:'nc',contact:'nct'};
  if(navMap[pg])document.getElementById(navMap[pg]).classList.add('active');
  if(pg==='shop'){renderCats();filterProds();}
  if(pg==='coa'){renderCOAs();}
  window.scrollTo(0,0);
}"""

NEW_GO = """function go(pg){
  ['home','shop','prod','about','coa','contact','auth','account','orders','admin'].forEach(id=>{const el=document.getElementById('p'+id);if(el)el.classList.remove('active');});
  const pgEl=document.getElementById('p'+pg);if(pgEl)pgEl.classList.add('active');
  document.querySelectorAll('[data-nav]').forEach(a=>a.classList.toggle('active',a.dataset.nav===pg));
  if(pg==='shop'){renderCats();filterProds();}
  if(pg==='coa'){renderCOAs();}
  window.scrollTo(0,0);
}
function openNav(){document.getElementById('navov').classList.add('open');document.getElementById('navdr').classList.add('open');}
function closeNav(){document.getElementById('navov').classList.remove('open');document.getElementById('navdr').classList.remove('open');}
function navGo(pg){go(pg);closeNav();}"""

if OLD_GO in text:
    text = text.replace(OLD_GO, NEW_GO, 1)
elif "function navGo" in text:
    pass
else:
    raise SystemExit("go() block not found")

p.write_text(text, encoding="utf-8")
print("mobile hamburger menu patched")
