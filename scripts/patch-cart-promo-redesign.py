"""Redesign cart promo cards to match reference: badges, CTAs, thin progress bars."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

OLD_CSS = """.cartpromos{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
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

NEW_CSS = """.cartpromos{display:flex;flex-direction:column;gap:10px;margin-bottom:14px}
.cartpromo{border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}
.cartpromo-body{padding:14px 14px 12px}
.cartpromo-top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}
.cartpromo-badge{font-size:9px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:4px 8px;border-radius:5px;line-height:1}
.cartpromo-status{font-size:9px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.cartpromo-headline{font-size:13px;font-weight:800;color:white;line-height:1.35;margin-bottom:5px}
.cartpromo-sub{font-size:11px;color:rgba(255,255,255,.42);line-height:1.45;margin-bottom:10px}
.cartpromo-cta{display:inline-block;font-size:12px;font-weight:700;cursor:pointer;text-decoration:none}
.cartpromo-bar{height:4px;background:rgba(255,255,255,.08)}
.cartpromo-bar-fill{height:100%;width:0;transition:width .45s cubic-bezier(.4,0,.2,1)}
.cartpromo-volume{border-color:rgba(100,160,220,.22);background:rgba(40,70,110,.18)}
.cartpromo-volume .cartpromo-badge{color:#8ec8ff;background:rgba(80,150,220,.15);border:1px solid rgba(100,170,240,.25)}
.cartpromo-volume .cartpromo-status{color:#8ec8ff}
.cartpromo-volume .cartpromo-cta{color:#7eb8f0}
.cartpromo-volume .cartpromo-bar-fill{background:linear-gradient(90deg,#4a8ec4,#7eb8f0)}
.cartpromo-gift{border-color:rgba(80,180,160,.22);background:rgba(30,80,70,.2)}
.cartpromo-gift .cartpromo-badge{color:#6fd4b8;background:rgba(60,160,130,.15);border:1px solid rgba(80,190,160,.25)}
.cartpromo-gift .cartpromo-status{color:#5fd4a8}
.cartpromo-gift .cartpromo-cta{color:#5fd4a8}
.cartpromo-gift .cartpromo-bar-fill{background:linear-gradient(90deg,#3a9a7a,#5fd4a8)}
.cartpromo-active.cartpromo-volume{border-color:rgba(100,180,240,.3)}
.cartpromo-active.cartpromo-gift{border-color:rgba(80,200,160,.3)}"""

OLD_JS = r"""function getCartPromos(items,deal){
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
    const text=away===1?`You're 1 vial away from ${next.l} — add 1 more for ${next.f} free vial${next.f>1?'s':''}!`:`Add ${away} more vial${away>1?'s':''} to unlock ${next.l} (${next.f} free). Lowest-priced vials free, each up to your order avg.`;
    promos.push({t:away===1?'near':'progress',icon:'🏷️',title,text,pct,cur:paid,goal:next.n,goalLabel:`${next.n} vials`});
  }
  const volFree=deal.volFree!=null?deal.volFree:Math.max(0,deal.freeCount-(deal.bacFree?1:0));
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

NEW_JS = r"""function getCartPromos(items,deal){
  const paid=paidVialCount(items);
  const bacIn=items.some(i=>i.id==='bacwater');
  const bacProd=PRODS.find(p=>p.id==='bacwater');
  const promos=[];
  const tiers=[{n:3,f:1,l:'Buy 3 Get 1 Free',total:4},{n:6,f:2,l:'Buy 6 Get 2 Free',total:8},{n:10,f:4,l:'Buy 10 Get 4 Free',total:14}];
  let cur=null,next=null;
  for(const tier of tiers){if(paid>=tier.n)cur=tier;else if(!next){next=tier;break;}}
  if(paid>=10){
    promos.push({kind:'volume',t:'active',badge:'VOLUME DEAL',status:'UNLOCKED',headline:'Buy 10 Get 4 Free — maximum deal applied!',sub:'4 free vials applied at checkout · lowest-priced vials free',pct:100});
  }else if(next){
    const from=cur?cur.n:0;
    const away=next.n-paid;
    const pct=tierProgress(paid,from,next.n);
    promos.push({
      kind:'volume',t:away===1?'near':'progress',badge:'VOLUME DEAL',status:away===1?'ALMOST THERE!':null,
      headline:away===1?`Add 1 more vial for ${next.f} FREE bonus vial${next.f>1?'s':''}!`:`Add ${away} more vials for ${next.f} FREE bonus vial${next.f>1?'s':''}!`,
      sub:`${next.l} — ${next.total} vials total`,pct,
      cta:'Add another vial →',ctaFn:"closeCart();go('shop')"
    });
  }
  if(bacProd){
    if(paid>=2){
      if(!bacIn){
        promos.push({kind:'gift',t:'click',badge:'FREE GIFT',status:'UNLOCKED!',headline:'FREE Bacteriostatic Water — 10mL unlocked!',sub:'Bacteriostatic Water 10mL added free at checkout',pct:100,cta:'Add free Bac Water →',ctaFn:'addFreeBacWater()'});
      }else{
        promos.push({kind:'gift',t:'active',badge:'FREE GIFT',status:'ADDED',headline:'FREE Bacteriostatic Water — 10mL included!',sub:'Applied free with your 2+ vial order',pct:100});
      }
    }else if(paid>0){
      const away=2-paid;
      promos.push({
        kind:'gift',t:away===1?'near':'progress',badge:'FREE GIFT',status:away===1?'ALMOST THERE!':null,
        headline:away===1?`You're 1 vial away from FREE Bacteriostatic Water — 10mL!`:`You're ${away} vials away from FREE Bacteriostatic Water — 10mL!`,
        sub:'Bacteriostatic Water 10mL added free at checkout',pct:promoProgress(paid,2),
        cta:'Browse vials →',ctaFn:"closeCart();go('shop')"
      });
    }
  }
  const volFree=deal.volFree!=null?deal.volFree:Math.max(0,deal.freeCount-(deal.bacFree?1:0));
  if(volFree>0&&deal.savings>0&&paid>=3){
    const vol=promos.find(p=>p.kind==='volume');
    if(vol&&vol.t!=='active'){
      vol.t='active';vol.status='APPLIED';vol.pct=100;
      vol.headline=`${volFree} free vial${volFree>1?'s':''} applied — $${deal.savings.toFixed(2)} off`;
      vol.sub='Lowest-priced vials free, each up to your order average';vol.cta=null;
    }
  }
  return promos;
}
function renderPromoHtml(promos){
  if(!promos.length)return '';
  return `<div class="cartpromos">${promos.map(p=>{
    const pct=Math.round(Math.min(100,Math.max(0,p.pct||0)));
    const status=p.status?`<span class="cartpromo-status">${p.status}</span>`:'<span></span>';
    const cta=p.cta?`<span class="cartpromo-cta" onclick="${p.ctaFn}">${p.cta}</span>`:'';
  return `<div class="cartpromo cartpromo-${p.kind} cartpromo-${p.t}"><div class="cartpromo-body"><div class="cartpromo-top"><span class="cartpromo-badge">${p.badge}</span>${status}</div><div class="cartpromo-headline">${p.headline}</div><div class="cartpromo-sub">${p.sub}</div>${cta}</div><div class="cartpromo-bar"><div class="cartpromo-bar-fill" style="width:${pct}%"></div></div></div>`;
  }).join('')}</div>`;
}"""

if OLD_CSS in text:
    text = text.replace(OLD_CSS, NEW_CSS, 1)
    print("css updated")
elif ".cartpromo-volume{" in text:
    print("css already updated")
else:
    raise SystemExit("css block not found")

if OLD_JS in text:
    text = text.replace(OLD_JS, NEW_JS, 1)
    print("js updated")
elif "kind:'volume'" in text:
    print("js already updated")
else:
    raise SystemExit("js block not found")

# Remove redundant deal summary box when promos show progress
OLD_RENDER = "  const dealSummary=deal.savings>0?`<div class=\"cartdeal\"><strong>Deal applied</strong><span class=\"cdealfree\">$${deal.savings.toFixed(2)} off</span>${deal.avgPaid>0?`<div style=\"font-size:11px;color:rgba(255,255,255,.28);margin-top:3px\">Avg paid $${deal.avgPaid.toFixed(2)}/vial</div>`:''}</div>`:'';\n  bd.innerHTML=`${renderPromoHtml(promos)}${dealSummary}${cart.map"
NEW_RENDER = "  bd.innerHTML=`${renderPromoHtml(promos)}${cart.map"
if OLD_RENDER in text:
    text = text.replace(OLD_RENDER, NEW_RENDER, 1)
    print("renderCart simplified")

p.write_text(text, encoding="utf-8")
print("done")
