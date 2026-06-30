"""Remove duplicate qty controls on product detail page."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

OLD_BLOCK = (
    '        <div class="qtyrow"><button class="qtybtn" onclick="chgQty(-1)">−</button><div class="qtyval" id="qtyval">1</div><button class="qtybtn" onclick="chgQty(1)">+</button></div>\n'
    '        <div id="pd-atc">${pdAtcInner()}</div>'
)
NEW_BLOCK = '        <div id="pd-atc">${pdAtcInner()}</div>'

if OLD_BLOCK in text:
    text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)

OLD_PD_ATC = (
    "function pdAtcInner(){if(!aProd)return'';const k=cartKey(aProd,aProd.sizes[aSz]);if(cartItemQty(k)>0)return qtyStepperHtml(k,false)+'<button class=\"atcbtn atcbtn-alt\" onclick=\"openCart()\">View Cart →</button>';return `<button class=\"atcbtn\" onclick=\"pdadd()\">Add to Cart</button>`;}"
)
NEW_PD_ATC = (
    "function pdPickQtyHtml(){return `<div class=\"qtystep qtystep-lg\"><button type=\"button\" class=\"qtybtn\" onclick=\"chgQty(-1)\">−</button><span class=\"qtyval\" id=\"qtyval\">${aQty}</span><button type=\"button\" class=\"qtybtn\" onclick=\"chgQty(1)\">+</button></div>`;}\n"
    "function pdAtcInner(){if(!aProd)return'';const k=cartKey(aProd,aProd.sizes[aSz]);if(cartItemQty(k)>0)return qtyStepperHtml(k,false)+'<button class=\"atcbtn atcbtn-alt\" onclick=\"openCart()\">View Cart →</button>';return pdPickQtyHtml()+`<button class=\"atcbtn\" onclick=\"pdadd()\">Add to Cart</button>`;}"
)

if "function pdPickQtyHtml" not in text and OLD_PD_ATC in text:
    text = text.replace(OLD_PD_ATC, NEW_PD_ATC, 1)

p.write_text(text, encoding="utf-8")
print("pd qty dedupe applied")
