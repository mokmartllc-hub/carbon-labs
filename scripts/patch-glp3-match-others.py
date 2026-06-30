"""Revert GLP-3 special image sizing — match all other products."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

text = text.replace(
    "\n.pc-fullimg .pimg img,.pdmainimg-full img,.pdthumb-full img{object-fit:contain!important;object-position:center center!important}\n.pc-fullimg .pimg,.pdmainimg-full,.pdthumb-full{background:#000}\n",
    "\n",
    1,
)

text = text.replace(
    "  const pcCls=p.id==='glp3rt'?'pc pc-fullimg':'pc';\n"
    "  return`<div class=\"${pcCls}\" data-pid=\"${p.id}\" onclick=\"showProd('${p.id}')\">",
    "  return`<div class=\"pc\" data-pid=\"${p.id}\" onclick=\"showProd('${p.id}')\">",
    1,
)

text = text.replace(
    '<div class="pdmainimg ${p.id===\'glp3rt\'?\'pdmainimg-full\':\'\'}"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>',
    '<div class="pdmainimg"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>',
    1,
)

text = text.replace(
    '<div class="pdthumb ${p.id===\'glp3rt\'?\'pdthumb-full \':\'\'}${i===aSz?\'active\':\'\'}" onclick="setSz(${i})">',
    '<div class="pdthumb ${i===aSz?\'active\':\'\'}" onclick="setSz(${i})">',
    1,
)

text = text.replace(
    "function setSz(i){aSz=i;const p=aProd,sz=p.sizes[i];const pm=document.querySelector('.pdmainimg');if(pm)pm.classList.toggle('pdmainimg-full',p.id==='glp3rt');document.getElementById('pdmainimg').src=sz.img;",
    "function setSz(i){aSz=i;const p=aProd,sz=p.sizes[i];document.getElementById('pdmainimg').src=sz.img;",
    1,
)

p.write_text(text, encoding="utf-8")
print("reverted glp3 special sizing")
