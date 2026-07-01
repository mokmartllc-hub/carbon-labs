"""Cart total = full subtotal; volume bonuses are extras, not subtracted from total."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"
text = p.read_text(encoding="utf-8")
before = len(text)

INSERT_AFTER = "function paidVialCount(items){return items.filter(i=>i.id!=='bacwater').reduce((s,i)=>s+i.qty,0);}"
INSERT = """function paidVialCount(items){return items.filter(i=>i.id!=='bacwater').reduce((s,i)=>s+i.qty,0);}
function cartSubtotal(items){return items.reduce((s,i)=>s+i.price*i.qty,0);}
function cartPayable(items,deal){
  let t=cartSubtotal(items);
  if(deal.bacFree)items.filter(i=>i.id==='bacwater').forEach(i=>{t-=i.price*i.qty;});
  return Math.max(0,t);
}"""

OLD_RENDER = """  const deal=calcDeal(cart),sub=cart.reduce((s,i)=>s+i.price*i.qty,0);
  const promos=getCartPromos(cart,deal);
  bd.innerHTML=`${renderPromoHtml(promos)}${cart.map(i=>{const fc=deal.freeKeys[i.k]||0;return`<div class="cartitem"><div class="cartimg"><img src="${i.img}" alt="${i.name}"></div><div class="cartinfo"><h4>${i.name}${fc?`<span class="cartfree">${fc}× FREE</span>`:''} </h4><p>${i.size}</p><div class="cart-qtyrow"><div class="cartprice">$${(i.price*i.qty).toFixed(2)}</div>${qtyStepperHtml(i.k,true)}</div></div></div>`;}).join('')}<div class="cartship">Free shipping · Ships in 24–48 business hours</div>`;
  document.getElementById('ctsub').textContent='$'+sub.toFixed(2);
  const sr=document.getElementById('csavrow');if(deal.savings>0){sr.style.display='flex';document.getElementById('ctsav').textContent='-$'+deal.savings.toFixed(2);}else sr.style.display='none';
  document.getElementById('cttot').textContent='$'+(sub-deal.savings).toFixed(2);ft.style.display='none:none';return;}"""

NEW_RENDER = """  const deal=calcDeal(cart),sub=cartSubtotal(cart),pay=cartPayable(cart,deal);
  const promos=getCartPromos(cart,deal);
  bd.innerHTML=`${renderPromoHtml(promos)}${cart.map(i=>{const fc=deal.freeKeys[i.k]||0;return`<div class="cartitem"><div class="cartimg"><img src="${i.img}" alt="${i.name}"></div><div class="cartinfo"><h4>${i.name}${fc?`<span class="cartfree">${fc}× FREE</span>`:''} </h4><p>${i.size}</p><div class="cart-qtyrow"><div class="cartprice">$${(i.price*i.qty).toFixed(2)}</div>${qtyStepperHtml(i.k,true)}</div></div></div>`;}).join('')}<div class="cartship">Free shipping · Ships in 24–48 business hours</div>`;
  document.getElementById('ctsub').textContent='$'+sub.toFixed(2);
  const sr=document.getElementById('csavrow'),volFree=deal.volFree||0,parts=[];
  if(volFree)parts.push(`${volFree} bonus vial${volFree>1?'s':''}`);
  if(deal.bacFree)parts.push('Free Bac Water');
  if(parts.length){sr.style.display='flex';document.getElementById('ctsav').textContent=parts.join(' · ');}else sr.style.display='none';
  document.getElementById('cttot').textContent='$'+pay.toFixed(2);ft.style.display='block';"""

# Fix typo in OLD_RENDER - I had a mistake. Let me use the actual content from grep.

OLD_RENDER = """  const deal=calcDeal(cart),sub=cart.reduce((s,i)=>s+i.price*i.qty,0);
  const promos=getCartPromos(cart,deal);
  bd.innerHTML=`${renderPromoHtml(promos)}${cart.map(i=>{const fc=deal.freeKeys[i.k]||0;return`<div class="cartitem"><div class="cartimg"><img src="${i.img}" alt="${i.name}"></div><div class="cartinfo"><h4>${i.name}${fc?`<span class="cartfree">${fc}× FREE</span>`:''} </h4><p>${i.size}</p><div class="cart-qtyrow"><div class="cartprice">$${(i.price*i.qty).toFixed(2)}</div>${qtyStepperHtml(i.k,true)}</div></div></div>`;}).join('')}<div class="cartship">Free shipping · Ships in 24–48 business hours</div>`;
  document.getElementById('ctsub').textContent='$'+sub.toFixed(2);
  const sr=document.getElementById('csavrow');if(deal.savings>0){sr.style.display='flex';document.getElementById('ctsav').textContent='-$'+deal.savings.toFixed(2);}else sr.style.display='none';
  document.getElementById('cttot').textContent='$'+(sub-deal.savings).toFixed(2);ft.style.display='block';"""

NEW_RENDER = """  const deal=calcDeal(cart),sub=cartSubtotal(cart),pay=cartPayable(cart,deal);
  const promos=getCartPromos(cart,deal);
  bd.innerHTML=`${renderPromoHtml(promos)}${cart.map(i=>{const fc=deal.freeKeys[i.k]||0;return`<div class="cartitem"><div class="cartimg"><img src="${i.img}" alt="${i.name}"></div><div class="cartinfo"><h4>${i.name}${fc?`<span class="cartfree">${fc}× FREE</span>`:''} </h4><p>${i.size}</p><div class="cart-qtyrow"><div class="cartprice">$${(i.price*i.qty).toFixed(2)}</div>${qtyStepperHtml(i.k,true)}</div></div></div>`;}).join('')}<div class="cartship">Free shipping · Ships in 24–48 business hours</div>`;
  document.getElementById('ctsub').textContent='$'+sub.toFixed(2);
  const sr=document.getElementById('csavrow'),volFree=deal.volFree||0,parts=[];
  if(volFree)parts.push(`${volFree} bonus vial${volFree>1?'s':''}`);
  if(deal.bacFree)parts.push('Free Bac Water');
  if(parts.length){sr.style.display='flex';document.getElementById('ctsav').textContent=parts.join(' · ');}else sr.style.display='none';
  document.getElementById('cttot').textContent='$'+pay.toFixed(2);ft.style.display='block';"""

OLD_FOOTER = '<div class="csav" id="csavrow" style="display:none"><span>Deal savings</span><span id="ctsav">-$0.00</span></div>'
NEW_FOOTER = '<div class="csav" id="csavrow" style="display:none"><span>Bonus included</span><span id="ctsav"></span></div>'

OLD_PROMO_MAX = "headline:volFree>0?`${volFree} bonus vial${volFree>1?'s':''} added on top — $${volSav.toFixed(2)} off`"
NEW_PROMO_MAX = "headline:volFree>0?`${volFree} bonus vial${volFree>1?'s':''} added on top at checkout`"

if "function cartPayable" not in text:
    if INSERT_AFTER not in text:
        raise SystemExit("paidVialCount anchor not found")
    text = text.replace(INSERT_AFTER, INSERT, 1)
else:
    print("cartPayable already present")

if OLD_RENDER not in text:
    if "cartPayable(cart,deal)" in text:
        print("renderCart already patched")
    else:
        raise SystemExit("renderCart block not found")
else:
    text = text.replace(OLD_RENDER, NEW_RENDER, 1)

if OLD_FOOTER in text:
    text = text.replace(OLD_FOOTER, NEW_FOOTER, 1)

if OLD_PROMO_MAX in text:
    text = text.replace(OLD_PROMO_MAX, NEW_PROMO_MAX, 1)

if len(text) < 10_000_000 or not text.rstrip().endswith("</html>"):
    raise SystemExit(f"REFUSING TO WRITE: truncated ({len(text)} bytes)")

p.write_text(text, encoding="utf-8")
print(f"patched cart total: {before} -> {len(text)} bytes")
