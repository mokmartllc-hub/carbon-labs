"""Add cart promo progress banners and free bac water CTA to index.html."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

CSS = """
.cartpromos{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
.cartpromo{display:flex;gap:12px;align-items:flex-start;padding:12px 14px;border-radius:10px;font-size:12px;line-height:1.5;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04)}
.cartpromo-icon{font-size:18px;line-height:1;flex-shrink:0;margin-top:1px}
.cartpromo-body{display:flex;flex-direction:column;gap:4px;min-width:0}
.cartpromo-body strong{font-size:12px;font-weight:800;color:white}
.cartpromo-body span{color:rgba(255,255,255,.55)}
.cartpromo-btn{margin-top:6px;align-self:flex-start;background:rgba(180,200,180,.15);border:1px solid rgba(160,200,160,.35);color:#b8e0b8;border-radius:8px;padding:8px 12px;font-size:11px;font-weight:800;cursor:pointer}
.cartpromo-btn:hover{background:rgba(180,200,180,.25)}
.cartpromo-click{border-color:rgba(160,200,160,.35);background:rgba(80,120,80,.12)}
.cartpromo-near{border-color:rgba(200,180,100,.25);background:rgba(200,160,60,.08)}
.cartpromo-near .cartpromo-body strong{color:#e8d080}
.cartpromo-active{border-color:rgba(160,200,160,.25);background:rgba(80,120,80,.1)}
.cartpromo-progress{border-color:rgba(255,255,255,.12)}
"""

if ".cartpromos{" not in text:
    text = text.replace(
        ".cdealfree{color:#aaaaaa;font-weight:700}",
        ".cdealfree{color:#aaaaaa;font-weight:700}" + CSS,
        1,
    )

HELPERS = r"""
function paidVialCount(items){return items.filter(i=>i.id!=='bacwater').reduce((s,i)=>s+i.qty,0);}
function getCartPromos(items,deal){
  const paid=paidVialCount(items);
  const bacIn=items.some(i=>i.id==='bacwater');
  const bacProd=PRODS.find(p=>p.id==='bacwater');
  const promos=[];
  const tiers=[{n:3,f:1,l:'Buy 3 Get 1'},{n:6,f:2,l:'Buy 6 Get 2'},{n:10,f:4,l:'Buy 10 Get 4'}];
  if(bacProd){
    if(paid>=2){
      if(!bacIn){
        promos.push({t:'click',icon:'💧',title:'Free Bac Water unlocked!',text:'You qualify for free bacteriostatic water with this order.',btn:'Add free Bac Water to cart',fn:'addFreeBacWater()'});
      }else{
        promos.push({t:'active',icon:'💧',title:'Free Bac Water included',text:'Buy 2+ vials deal applied — Bac Water is free.'});
      }
    }else if(paid===1){
      promos.push({t:'near',icon:'💧',title:'1 vial away from free Bac Water',text:'Add 1 more peptide vial to unlock free bacteriostatic water.'});
    }
  }
  let cur=null,next=null;
  for(const tier of tiers){if(paid>=tier.n)cur=tier;else if(!next){next=tier;break;}}
  if(paid>=10){
    promos.push({t:'active',icon:'🎉',title:'Buy 10 Get 4 unlocked!',text:'Maximum volume deal — 4 free vials applied at checkout.'});
  }else if(cur&&next){
    const away=next.n-paid;
    promos.push({t:away===1?'near':'progress',icon:'🏷️',title:cur.l+' active',text:away===1?`You're 1 vial away from ${next.l} — add 1 more for ${next.f} free vial${next.f>1?'s':''}!`:`Add ${away} more vial${away>1?'s':''} to unlock ${next.l} (${next.f} free).`});
  }else if(next){
    const away=next.n-paid;
    promos.push({t:away===1?'near':'progress',icon:'🏷️',title:away===1?`1 vial from ${next.l}`:'Volume deal',text:away===1?`You're 1 vial away from ${next.l} — add 1 more for a free vial!`:`Add ${away} more vial${away>1?'s':''} to unlock ${next.l}.`});
  }
  const volFree=Math.max(0,deal.freeCount-(deal.bacFree?1:0));
  if(volFree>0&&deal.savings>0){
    promos.unshift({t:'active',icon:'✓',title:'Volume savings applied',text:`${volFree} free vial${volFree>1?'s':''} · $${deal.savings.toFixed(2)} off your order`});
  }
  return promos;
}
function renderPromoHtml(promos){
  if(!promos.length)return '';
  return `<div class="cartpromos">${promos.map(p=>{
    const btn=p.btn?`<button type="button" class="cartpromo-btn" onclick="${p.fn}">${p.btn}</button>`:'';
    return `<div class="cartpromo cartpromo-${p.t}"><div class="cartpromo-icon">${p.icon}</div><div class="cartpromo-body"><strong>${p.title}</strong><span>${p.text}</span>${btn}</div></div>`;
  }).join('')}</div>`;
}
function addFreeBacWater(){
  const p=PRODS.find(x=>x.id==='bacwater');
  if(!p)return;
  if(cart.find(i=>i.id==='bacwater')){openCart();return;}
  addC(p,p.sizes[0],1);
}
"""

OLD_RENDER = (
    "function renderCart(){\n"
    "  const bd=document.getElementById('cartbd'),ft=document.getElementById('cartft');\n"
    "  if(!cart.length){bd.innerHTML='<div class=\"cartempty\"><p>Your cart is empty.</p><p style=\"margin-top:8px;font-size:12px\">Add a product to get started.</p></div>';ft.style.display='none';return;}\n"
    "  const deal=calcDeal(cart),sub=cart.reduce((s,i)=>s+i.price*i.qty,0),tu=cart.reduce((s,i)=>s+i.qty,0);\n"
    "  let pn='';const paidVialCount=cart.filter(i=>i.id!=='bacwater').reduce((s,i)=>s+i.qty,0);\n"
    "  if(tu<3)pn=`Add ${3-tu} more to unlock Buy 3 Get 1`;else if(tu<6)pn=`Add ${6-tu} more to unlock Buy 6 Get 2`;else if(tu<10)pn=`Add ${10-tu} more to unlock Buy 10 Get 4`;else pn='🎉 Buy 10 Get 4 — max deal unlocked!';\n"
    "  const bacPromo=paidVialCount>=2?'<div class=\"cartship\" style=\"color:rgba(200,200,200,.8)\">💧 Buy 2 deal active — free Bac Water included!</div>':'';\n"
    "  bd.innerHTML=`${bacPromo}<div class=\"cartdeal\"><strong>Volume Deal</strong>${deal.freeCount>0?`<span class=\"cdealfree\">✓ ${deal.freeCount} free vial${deal.freeCount>1?'s':''} · saving $${deal.savings.toFixed(2)}</span><div style=\"font-size:11px;color:rgba(255,255,255,.28);margin-top:3px\">Avg paid $${deal.avgPaid.toFixed(2)}/vial</div>`:`<span style=\"color:rgba(255,255,255,.38)\">${pn}</span>`}</div>${cart.map(i=>{const fc=deal.freeKeys[i.k]||0;return`<div class=\"cartitem\"><div class=\"cartimg\"><img src=\"${i.img}\" alt=\"${i.name}\"></div><div class=\"cartinfo\"><h4>${i.name}${fc?`<span class=\"cartfree\">${fc}× FREE</span>`:''} </h4><p>${i.size}</p><div class=\"cart-qtyrow\"><div class=\"cartprice\">$${(i.price*i.qty).toFixed(2)}</div>${qtyStepperHtml(i.k,true)}</div></div></div>`;}).join('')}<div class=\"cartship\">Free shipping · Ships in 24–48 business hours</div>`;\n"
    "  document.getElementById('ctsub').textContent='$'+sub.toFixed(2);\n"
    "  const sr=document.getElementById('csavrow');if(deal.savings>0){sr.style.display='flex';document.getElementById('ctsav').textContent='-$'+deal.savings.toFixed(2);}else sr.style.display='none';\n"
    "  document.getElementById('cttot').textContent='$'+(sub-deal.savings).toFixed(2);ft.style.display='block';\n"
    "}"
)

NEW_RENDER = (
    "function renderCart(){\n"
    "  const bd=document.getElementById('cartbd'),ft=document.getElementById('cartft');\n"
    "  if(!cart.length){bd.innerHTML='<div class=\"cartempty\"><p>Your cart is empty.</p><p style=\"margin-top:8px;font-size:12px\">Add a product to get started.</p></div>';ft.style.display='none';return;}\n"
    "  const deal=calcDeal(cart),sub=cart.reduce((s,i)=>s+i.price*i.qty,0);\n"
    "  const promos=getCartPromos(cart,deal);\n"
    "  const dealSummary=deal.savings>0?`<div class=\"cartdeal\"><strong>Deal applied</strong><span class=\"cdealfree\">$${deal.savings.toFixed(2)} off</span>${deal.avgPaid>0?`<div style=\"font-size:11px;color:rgba(255,255,255,.28);margin-top:3px\">Avg paid $${deal.avgPaid.toFixed(2)}/vial</div>`:''}</div>`:'';\n"
    "  bd.innerHTML=`${renderPromoHtml(promos)}${dealSummary}${cart.map(i=>{const fc=deal.freeKeys[i.k]||0;return`<div class=\"cartitem\"><div class=\"cartimg\"><img src=\"${i.img}\" alt=\"${i.name}\"></div><div class=\"cartinfo\"><h4>${i.name}${fc?`<span class=\"cartfree\">${fc}× FREE</span>`:''} </h4><p>${i.size}</p><div class=\"cart-qtyrow\"><div class=\"cartprice\">$${(i.price*i.qty).toFixed(2)}</div>${qtyStepperHtml(i.k,true)}</div></div></div>`;}).join('')}<div class=\"cartship\">Free shipping · Ships in 24–48 business hours</div>`;\n"
    "  document.getElementById('ctsub').textContent='$'+sub.toFixed(2);\n"
    "  const sr=document.getElementById('csavrow');if(deal.savings>0){sr.style.display='flex';document.getElementById('ctsav').textContent='-$'+deal.savings.toFixed(2);}else sr.style.display='none';\n"
    "  document.getElementById('cttot').textContent='$'+(sub-deal.savings).toFixed(2);ft.style.display='block';\n"
    "}"
)

patches = []

if "function getCartPromos" not in text:
    text = text.replace(
        "function renderCart(){",
        HELPERS + "\nfunction renderCart(){",
        1,
    )
    patches.append("helpers")

if OLD_RENDER in text:
    text = text.replace(OLD_RENDER, NEW_RENDER, 1)
    patches.append("renderCart")
elif "renderPromoHtml(promos)" in text:
    patches.append("renderCart-already-patched")
else:
    patches.append("renderCart-NOT-FOUND")

p.write_text(text, encoding="utf-8")
print("patched:", ", ".join(patches) or "nothing")
print("size", p.stat().st_size)
