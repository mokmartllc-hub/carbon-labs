"""Add admin panel page, styles, and scripts to public/index.html."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"
text = p.read_text(encoding="utf-8")
patches = []

ADMIN_CSS = """
/* admin panel */
.admin-wrap{max-width:1200px;margin:0 auto;padding:48px 36px 80px}
.admin-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:24px}
.admin-tab{padding:10px 18px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:rgba(255,255,255,.45);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:8px;cursor:pointer;transition:all .2s}
.admin-tab:hover{color:rgba(255,255,255,.75);border-color:rgba(255,255,255,.15)}
.admin-tab.active{color:white;background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.22)}
.admin-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin-bottom:20px}
.admin-stat{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:12px;padding:18px;text-align:center}
.admin-stat .n{font-size:22px;font-weight:800;color:var(--a2)}
.admin-stat .l{font-size:11px;color:rgba(255,255,255,.4);margin-top:4px;text-transform:uppercase;letter-spacing:.05em}
.admin-alert{background:rgba(200,120,80,.12);border:1px solid rgba(200,120,80,.25);color:#e8b090;padding:12px 16px;border-radius:10px;font-size:13px;margin-bottom:16px}
.admin-note{font-size:13px;color:rgba(255,255,255,.4);margin-bottom:16px}
.admin-table-wrap{overflow-x:auto;border:1px solid rgba(255,255,255,.09);border-radius:12px}
.admin-table{width:100%;border-collapse:collapse;font-size:13px}
.admin-table th{text-align:left;padding:12px 16px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:rgba(255,255,255,.35);border-bottom:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03)}
.admin-table td{padding:14px 16px;color:rgba(255,255,255,.7);border-bottom:1px solid rgba(255,255,255,.05);vertical-align:top}
.admin-table tr:last-child td{border-bottom:none}
.admin-sub{font-size:11px;color:rgba(255,255,255,.35);margin-top:2px}
.admin-select{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:white;padding:6px 10px;border-radius:6px;font-size:12px}
.admin-empty{text-align:center;padding:48px 24px;color:rgba(255,255,255,.4);font-size:14px}
.admin-toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.admin-btn-sm{padding:10px 18px;font-size:12px}
.admin-btn-ghost{background:transparent;border:1px solid rgba(255,255,255,.15)}
.admin-btn-danger{background:rgba(180,60,60,.25);border-color:rgba(180,60,60,.4)}
.admin-link-btn{background:none;border:none;color:var(--a2);font-size:12px;font-weight:700;cursor:pointer;padding:4px 0}
.admin-card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:24px 28px;margin-bottom:12px}
.admin-card h2{font-size:16px;font-weight:800;color:white;margin-bottom:16px}
.admin-card-sm{padding:16px 20px}
.admin-card-hd{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:white}
.admin-textarea{min-height:80px;resize:vertical}
.admin-size-row{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:8px}
@media(max-width:900px){.admin-size-row{grid-template-columns:1fr 1fr}}
"""

ADMIN_PAGE = """
  <!-- ===== ADMIN ===== -->
  <div id="padmin" class="page">
    <div class="pg-hero" style="padding:72px 36px 48px">
      <div class="pg-hero-inner">
        <div class="pg-eyebrow">Store Management</div>
        <h1 class="pg-title">Admin <span class="hl">Panel</span></h1>
        <p class="pg-sub">Manage products, orders, stock, and customer messages.</p>
      </div>
    </div>
    <div class="admin-wrap"><div id="admin-root"></div></div>
    <div class="pg-footer-mini"></div>
  </div>
"""

if "/* admin panel */" not in text:
    text = text.replace("</style>", ADMIN_CSS + "</style>", 1)
    patches.append("css")

marker = '    <div class="pg-footer-mini"></div>\n  </div>\n\n</div>\n\n<div class="cartov"'
if 'id="padmin"' not in text and marker in text:
    text = text.replace(
        marker,
        '    <div class="pg-footer-mini"></div>\n  </div>\n' + ADMIN_PAGE + "\n</div>\n\n<div class=\"cartov\"",
        1,
    )
    patches.append("page")

old_go = "['home','shop','prod','about','coa','contact','auth','account','orders'].forEach"
new_go = "['home','shop','prod','about','coa','contact','auth','account','orders','admin'].forEach"
if old_go in text and "'admin'" not in text.split("function go")[1][:200]:
    text = text.replace(old_go, new_go, 1)
    patches.append("go-list")

if "/catalog.js" not in text:
    text = text.replace(
        '<script src="/api.js"></script>',
        '<script src="/catalog.js"></script>\n<script src="/api.js"></script>\n<script src="/admin.js"></script>',
        1,
    )
    patches.append("scripts")

p.write_text(text, encoding="utf-8")
print("patched:", ", ".join(patches) or "nothing needed")
print("size", p.stat().st_size, "bytes")
