"""Show full GLP-3 vial (no crop) on listing and product pages."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

CSS = """
.pc-fullimg .pimg img,.pdmainimg-full img,.pdthumb-full img{object-fit:contain!important;object-position:center center!important}
.pc-fullimg .pimg,.pdmainimg-full,.pdthumb-full{background:#000}
"""

if ".pc-fullimg .pimg img" not in text:
    text = text.replace(
        ".pimg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 20%;display:block;transition:transform .3s ease}",
        ".pimg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 20%;display:block;transition:transform .3s ease}"
        + CSS,
        1,
    )

OLD_PCARD_RETURN = (
    '  return`<div class="pc" data-pid="${p.id}" onclick="showProd(\'${p.id}\')"><div class="pimg"><img src="${sz.img}" alt="${p.name}" loading="lazy">${p.badge?`<div class="pbadge">${p.badge}</div>`:\'\'}</div>'
)
NEW_PCARD_RETURN = (
    '  const pcCls=p.id===\'glp3rt\'?\'pc pc-fullimg\':\'pc\';\n'
    '  return`<div class="${pcCls}" data-pid="${p.id}" onclick="showProd(\'${p.id}\')"><div class="pimg"><img src="${sz.img}" alt="${p.name}" loading="lazy">${p.badge?`<div class="pbadge">${p.badge}</div>`:\'\'}</div>'
)

if "pc-fullimg" not in text and OLD_PCARD_RETURN in text:
    text = text.replace(OLD_PCARD_RETURN, NEW_PCARD_RETURN, 1)

OLD_PDMAIN = '<div class="pdmainimg"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>'
NEW_PDMAIN = '<div class="pdmainimg ${p.id===\'glp3rt\'?\'pdmainimg-full\':\'\'}"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>'

if "pdmainimg-full" not in text and OLD_PDMAIN in text:
    text = text.replace(OLD_PDMAIN, NEW_PDMAIN, 1)

OLD_THUMBS = '`${p.sizes.map((s,i)=>`<div class="pdthumb ${i===aSz?\'active\':\'\'}" onclick="setSz(${i})"><img src="${s.img}" alt="${p.name} ${s.l}"></div>`).join(\'\')}`'
NEW_THUMBS = '`${p.sizes.map((s,i)=>`<div class="pdthumb ${p.id===\'glp3rt\'?\'pdthumb-full \':\'\'}${i===aSz?\'active\':\'\'}" onclick="setSz(${i})"><img src="${s.img}" alt="${p.name} ${s.l}"></div>`).join(\'\')}`'

if "pdthumb-full" not in text and OLD_THUMBS in text:
    text = text.replace(OLD_THUMBS, NEW_THUMBS, 1)

# Toggle full-img class when switching GLP-3 sizes on product page
OLD_SETSZ = "function setSz(i){aSz=i;const p=aProd,sz=p.sizes[i];document.getElementById('pdmainimg').src=sz.img;"
NEW_SETSZ = "function setSz(i){aSz=i;const p=aProd,sz=p.sizes[i];const pm=document.querySelector('.pdmainimg');if(pm)pm.classList.toggle('pdmainimg-full',p.id==='glp3rt');document.getElementById('pdmainimg').src=sz.img;"

if "pm.classList.toggle('pdmainimg-full'" not in text and OLD_SETSZ in text:
    text = text.replace(OLD_SETSZ, NEW_SETSZ, 1)

p.write_text(text, encoding="utf-8")
print("glp3 full-vial display patch applied")
