"""Replace cart promo banners with fill progress bars toward next deal."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

OLD_CSS = """.cartpromos{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
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
.cartpromo-progress{border-color:rgba(255,255,255,.12)}"""

NEW_CSS = """.cartpromos{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
.cartpromo{padding:12px 14px;border-radius:10px;font-size:12px;line-height:1.5;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04)}
.cartpromo-hd{display:flex;gap:10px;align-items:center;margin-bottom:8px}
.cartpromo-icon{font-size:16px;line-height:1;flex-shrink:0}
.cartpromo-title{font-size:12px;font-weight:800;color:white;flex:1;min-width:0}
.cartpromo-text{font-size:11px;color:rgba(255,255,255,.5);margin-bottom:8px;line-height:1.45}
.cartpromo-bar{height:7px;background:rgba(255,255,255,.08);border-radius:99px;overflow:hidden}
.cartpromo-bar-fill{height:100%;border-radius:99px;width:0;transition:width .4s cubic-bezier(.4,0,.2,1);background:linear-gradient(90deg,rgba(255,255,255,.22),rgba(255,255,255,.5))}
.cartpromo-bar-meta{display:flex;justify-content:space-between;align-items:center;margin-top:6px;font-size:10px;color:rgba(255,255,255,.35);font-weight:600}
.cartpromo-bar-meta em{font-style:normal;color:rgba(255,255,255,.55)}
.cartpromo-btn{margin-top:10px;width:100%;background:rgba(180,200,180,.15);border:1px solid rgba(160,200,160,.35);color:#b8e0b8;border-radius:8px;padding:9px 12px;font-size:11px;font-weight:800;cursor:pointer}
.cartpromo-btn:hover{background:rgba(180,200,180,.25)}
.cartpromo-click{border-color:rgba(160,200,160,.35);background:rgba(80,120,80,.12)}
.cartpromo-click .cartpromo-bar-fill{background:linear-gradient(90deg,rgba(120,180,120,.65),#b8e0b8)}
.cartpromo-near{border-color:rgba(200,180,100,.25);background:rgba(200,160,60,.08)}
.cartpromo-near .cartpromo-title{color:#e8d080}
.cartpromo-near .cartpromo-bar-fill{background:linear-gradient(90deg,rgba(200,170,80,.55),#e8d080)}
.cartpromo-active{border-color:rgba(160,200,160,.25);background:rgba(80,120,80,.1)}
.cartpromo-active .cartpromo-title{color:#b8e0b8}
.cartpromo-active .cartpromo-bar-fill{background:linear-gradient(90deg,rgba(120,180,120,.65),#b8e0b8)}
.cartpromo-progress .cartpromo-bar-fill{background:linear-gradient(90deg,rgba(180,180,180,.35),rgba(255,255,255,.55))}"""

OLD_HELPERS = r"""function paidVialCount(items){return items.filter(i=>i.id!=='bacwater').reduce((s,i)=>s+i.qty,0);}
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
}"""

NEW_HELPERS = r"""function paidVialCount(items){return items.filter(i=>i.id!=='bacwater').reduce((s,i)=>s+i.qty,0);}
function promoProgress(cur,goal){if(!goal)return 100;return Math.min(100,Math.max(0,(cur/goal)*100));}
function tierProgress(paid,from,goal){if(goal<=from)return 100;return Math.min(100,Math.max(0,((paid-from)/(goal-from))*100));}
function getCartPromos(items,deal){
  const paid=paidVialCount(items);
  const bacIn=items.some(i=>i.id==='bacwater');
  const bacProd=PRODS.find(p=>p.id==='bacwater');
  const promos=[];
  const tiers=[{n:3,f:1,l:'Buy 3 Get 1'},{n:6,f:2,l:'Buy 6 Get 2'},{n:10,f:4,l:'Buy 10 Get 4'}];
  if(bacProd){
    if(paid>=2){
      if(!bacIn){
        promos.push({t:'click',icon:'💧',title:'Free Bac Water unlocked!',text:'You qualify for free bacteriostatic water with this order.',btn:'Add free Bac Water to cart',fn:'addFreeBacWater()',pct:100,cur:2,goal:2,goalLabel:'2 vials'});
      }else{
        promos.push({t:'active',icon:'💧',title:'Free Bac Water included',text:'Buy 2+ vials deal applied — Bac Water is free.',pct:100,cur:2,goal:2,goalLabel:'2 vials'});
      }
    }else if(paid>0){
      const away=2-paid;
      promos.push({t:away===1?'near':'progress',icon:'💧',title:away===1?'1 vial away from free Bac Water':'Free Bac Water',text:away===1?'Add 1 more peptide vial to unlock free bacteriostatic water.':`Add ${away} more vial${away>1?'s':''} for free Bac Water.`,pct:promoProgress(paid,2),cur:paid,goal:2,goalLabel:'2 vials'});
    }
  }
  let cur=null,next=null;
  for(const tier of tiers){if(paid>=tier.n)cur=tier;else if(!next){next=tier;break;}}
  if(paid>=10){
    promos.push({t:'active',icon:'🎉',title:'Buy 10 Get 4 unlocked!',text:'Maximum volume deal — 4 free vials applied at checkout.',pct:100,cur:10,goal:10,goalLabel:'10 vials'});
  }else if(next){
    const from=cur?cur.n:0;
    const away=next.n-paid;
    const pct=tierProgress(paid,from,next.n);
    const title=cur?(away===1?`1 vial from ${next.l}`:`${cur.l} active`):away===1?`1 vial from ${next.l}`:'Volume deal';
    const text=away===1?`You're 1 vial away from ${next.l} — add 1 more for ${next.f} free vial${next.f>1?'s':''}!`:`Add ${away} more vial${away>1?'s':''} to unlock ${next.l} (${next.f} free).`;
    promos.push({t:away===1?'near':'progress',icon:'🏷️',title,text,pct,cur:paid,goal:next.n,goalLabel:`${next.n} vials`});
  }
  const volFree=Math.max(0,deal.freeCount-(deal.bacFree?1:0));
  if(volFree>0&&deal.savings>0){
    promos.unshift({t:'active',icon:'✓',title:'Volume savings applied',text:`${volFree} free vial${volFree>1?'s':''} · $${deal.savings.toFixed(2)} off your order`,pct:100,cur:paid,goal:paid,goalLabel:'applied'});
  }
  return promos;
}
function renderPromoHtml(promos){
  if(!promos.length)return '';
  return `<div class="cartpromos">${promos.map(p=>{
    const pct=Math.round(Math.min(100,Math.max(0,p.pct||0)));
    const meta=(p.cur!=null&&p.goal!=null)?`<div class="cartpromo-bar-meta"><span><em>${p.cur}</em> / ${p.goal} vials</span><span>${pct}%</span></div>`:'';
    const bar=`<div class="cartpromo-bar"><div class="cartpromo-bar-fill" style="width:${pct}%"></div></div>${meta}`;
    const btn=p.btn?`<button type="button" class="cartpromo-btn" onclick="${p.fn}">${p.btn}</button>`:'';
    return `<div class="cartpromo cartpromo-${p.t}"><div class="cartpromo-hd"><span class="cartpromo-icon">${p.icon}</span><span class="cartpromo-title">${p.title}</span></div><div class="cartpromo-text">${p.text}</div>${bar}${btn}</div>`;
  }).join('')}</div>`;
}"""

patches = []

if OLD_CSS in text:
    text = text.replace(OLD_CSS, NEW_CSS, 1)
    patches.append("css")
elif ".cartpromo-bar{" in text:
    patches.append("css-already")
else:
    patches.append("css-NOT-FOUND")

if OLD_HELPERS in text:
    text = text.replace(OLD_HELPERS, NEW_HELPERS, 1)
    patches.append("helpers")
elif "function promoProgress" in text:
    patches.append("helpers-already")
else:
    patches.append("helpers-NOT-FOUND")

p.write_text(text, encoding="utf-8")
print("patched:", ", ".join(patches))
