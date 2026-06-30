from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

old_pcard = (
    "function pcard(p){\n"
    "  const sz=p.sizes[0],fr=p.sizes.length>1?'<span class=\"fr\">from</span>':'';\n"
    "  return`<div class=\"pc\" data-pid=\"${p.id}\" onclick=\"showProd('${p.id}')\">"
)
new_pcard = (
    "function pcard(p){\n"
    "  const sz=p.sizes[0],fr=p.sizes.length>1?'<span class=\"fr\">from</span>':'';\n"
    "  const pcCls=p.id==='glp3rt'?'pc pc-fullimg':'pc';\n"
    "  return`<div class=\"${pcCls}\" data-pid=\"${p.id}\" onclick=\"showProd('${p.id}')\">"
)

if "const pcCls=p.id==='glp3rt'" not in text and old_pcard in text:
    text = text.replace(old_pcard, new_pcard, 1)
    print("pcard patched")
else:
    print("pcard skip", "const pcCls" in text)

text = text.replace(
    '<div class="pdmainimg"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>',
    '<div class="pdmainimg ${p.id===\'glp3rt\'?\'pdmainimg-full\':\'\'}"><img src="${sz.img}" alt="${p.name} ${sz.l}" id="pdmainimg"></div>',
    1,
)
text = text.replace(
    '<div class="pdthumb ${i===aSz?\'active\':\'\'}" onclick="setSz(${i})">',
    '<div class="pdthumb ${p.id===\'glp3rt\'?\'pdthumb-full \':\'\'}${i===aSz?\'active\':\'\'}" onclick="setSz(${i})">',
    1,
)

p.write_text(text, encoding="utf-8")
print("done")
