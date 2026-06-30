"""Mobile product page: full vial image + vertical mg variant pills (Ascend-style)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"
text = p.read_text(encoding="utf-8")
before = len(text)

PD_CSS_OLD = """.pdmainimg{border-radius:16px;overflow:hidden;aspect-ratio:3/4;position:relative;border:1px solid rgba(255,255,255,.08);background:#111111}
.pdmainimg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 20%;display:block;transition:transform .3s ease}
.pdmainimg:hover img{transform:scale(1.03)}
.pdthumbs{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}"""

PD_CSS_NEW = """.pdmainimg{border-radius:16px;overflow:hidden;aspect-ratio:3/4;position:relative;border:1px solid rgba(255,255,255,.08);background:#111111}
.pdmainimg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 20%;display:block;transition:opacity .2s ease,transform .3s ease}
.pdmainimg:hover img{transform:scale(1.03)}
.pdhero{display:block}
.pdvars{display:none}
.pd-mobile-hd{display:none}
.pdthumbs{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}"""

MOBILE_PD_BLOCK = """  .cartdr{width:100%;max-width:100%}
  .pdpage{padding:12px 14px 40px}
  .pdtop{grid-template-columns:1fr;gap:18px;margin-bottom:32px}
  .pd-mobile-hd{display:block;margin-bottom:4px}
  .pd-mobile-hd h1{font-size:26px;font-weight:900;color:white;letter-spacing:-.03em;margin-bottom:4px}
  .pd-size-lbl{font-size:14px;color:rgba(255,255,255,.55);margin-bottom:14px}
  .pd-size-lbl span{color:white;font-weight:700}
  .pd-desktop-hd{display:none}
  .pdhero{display:flex;align-items:center;gap:14px;margin-bottom:4px}
  .pdvars{display:flex;flex-direction:column;gap:10px;flex-shrink:0}
  .pdvar{width:54px;height:54px;border-radius:50%;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.06);color:rgba(255,255,255,.75);font-size:11px;font-weight:800;cursor:pointer;padding:0;line-height:1;transition:background .15s,border-color .15s,color .15s}
  .pdvar.active{background:#fff;color:#111;border-color:#fff}
  .pdmainimg{aspect-ratio:auto;flex:1;min-width:0;height:min(52vh,440px);max-height:440px;border-radius:14px}
  .pdmainimg img{object-fit:contain;object-position:center center}
  .pdmainimg:hover img{transform:none}
  .pdthumbs{display:none!important}
  .szsizes{display:none!important}
  .pdright h1{display:none}
  .pdright .pdsubt:first-of-type{display:none}
  .pdright .szlabel{display:none}
  .pdprice{font-size:28px;margin-top:4px}
}"""

RENDER_OLD = """    <div class="pdtop">
      <div>
        <div class="pdmainimg"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>
        ${p.sizes.length>1?`<div class="pdthumbs">${p.sizes.map((s,i)=>`<div class="pdthumb ${i===aSz?'active':''}" onclick="setSz(${i})"><img src="${s.img}" alt="${p.name} ${s.l}"></div>`).join('')}</div>`:'<div style="height:12px"></div>'}
      </div>
      <div class="pdright">
        <h1>${p.name}</h1><div class="pdsubt">${p.tag}</div>
        ${p.sizes.length>1?`<div class="szlabel">Size <span style="color:rgba(255,255,255,.45);font-weight:400;text-transform:none;letter-spacing:0;font-size:11px" id="szsel">— ${sz.l}</span></div><div class="szsizes">${p.sizes.map((s,i)=>`<button class="szbtn ${i===aSz?'active':''}" onclick="setSz(${i})">${s.l}</button>`).join('')}</div>`:'<div style="margin-bottom:16px"></div>'}"""

RENDER_NEW = """    <div class="pd-mobile-hd">
      <h1>${p.name}</h1>
      <div class="pdsubt">${p.tag}</div>
      ${p.sizes.length>1?`<div class="pd-size-lbl">Size: <span id="szsel">${sz.l}</span></div>`:''}
    </div>
    <div class="pdtop">
      <div class="pdleft">
        <div class="pdhero">
          ${p.sizes.length>1?`<div class="pdvars">${p.sizes.map((s,i)=>`<button type="button" class="pdvar ${i===aSz?'active':''}" onclick="setSz(${i})">${s.l}</button>`).join('')}</div>`:''}
          <div class="pdmainimg"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>
        </div>
        ${p.sizes.length>1?`<div class="pdthumbs">${p.sizes.map((s,i)=>`<div class="pdthumb ${i===aSz?'active':''}" onclick="setSz(${i})"><img src="${s.img}" alt="${p.name} ${s.l}"></div>`).join('')}</div>`:'<div style="height:12px"></div>'}
      </div>
      <div class="pdright">
        <div class="pd-desktop-hd"><h1>${p.name}</h1><div class="pdsubt">${p.tag}</div></div>
        ${p.sizes.length>1?`<div class="szlabel">Size <span style="color:rgba(255,255,255,.45);font-weight:400;text-transform:none;letter-spacing:0;font-size:11px" id="szsel-d">— ${sz.l}</span></div><div class="szsizes">${p.sizes.map((s,i)=>`<button class="szbtn ${i===aSz?'active':''}" onclick="setSz(${i})">${s.l}</button>`).join('')}</div>`:'<div style="margin-bottom:16px"></div>'}"""

SETSZ_OLD = "function setSz(i){aSz=i;const p=aProd,sz=p.sizes[i];document.getElementById('pdmainimg').src=sz.img;document.getElementById('pdprice').textContent='$'+sz.p+'.00';document.querySelectorAll('.szbtn').forEach((b,j)=>b.classList.toggle('active',j===i));document.querySelectorAll('.pdthumb').forEach((b,j)=>b.classList.toggle('active',j===i));const ssl=document.getElementById('szsel');if(ssl)ssl.textContent='— '+sz.l;const bs=document.getElementById('batchspan');if(bs)bs.textContent=sz.batch;updPdAtc();}"

SETSZ_NEW = "function setSz(i){aSz=i;const p=aProd,sz=p.sizes[i];const img=document.getElementById('pdmainimg');if(img){img.style.opacity='0.4';setTimeout(()=>{img.src=sz.img;img.style.opacity='1';},120);}document.getElementById('pdprice').textContent='$'+sz.p+'.00';document.querySelectorAll('.szbtn').forEach((b,j)=>b.classList.toggle('active',j===i));document.querySelectorAll('.pdvar').forEach((b,j)=>b.classList.toggle('active',j===i));document.querySelectorAll('.pdthumb').forEach((b,j)=>b.classList.toggle('active',j===i));const ssl=document.getElementById('szsel');if(ssl)ssl.textContent=sz.l;const ssd=document.getElementById('szsel-d');if(ssd)ssd.textContent='— '+sz.l;const bs=document.getElementById('batchspan');if(bs)bs.textContent=sz.batch;updPdAtc();}"

ANCHOR = "  .cartdr{width:100%;max-width:100%}\n}"

if PD_CSS_OLD not in text:
    if ".pdvars{display:none}" in text:
        print("pd css ok")
    else:
        raise SystemExit("pd css block not found")

if RENDER_OLD not in text:
    if "pd-mobile-hd" in text:
        print("renderPD ok")
    else:
        raise SystemExit("renderPD block not found")

if PD_CSS_OLD in text:
    text = text.replace(PD_CSS_OLD, PD_CSS_NEW, 1)

if RENDER_OLD in text:
    text = text.replace(RENDER_OLD, RENDER_NEW, 1)

if SETSZ_OLD in text:
    text = text.replace(SETSZ_OLD, SETSZ_NEW, 1)
elif "document.querySelectorAll('.pdvar')" in text:
    print("setSz ok")
else:
    raise SystemExit("setSz not found")

if ".pd-mobile-hd{display:block" not in text:
    if ANCHOR not in text:
        raise SystemExit("mobile anchor not found")
    text = text.replace(ANCHOR, MOBILE_PD_BLOCK, 1)
else:
    print("mobile pd css ok")

if len(text) < 10_000_000 or not text.rstrip().endswith("</html>"):
    raise SystemExit(f"REFUSING TO WRITE: truncated ({len(text)} bytes)")

p.write_text(text, encoding="utf-8")
print(f"patched mobile product page: {before} -> {len(text)} bytes")
