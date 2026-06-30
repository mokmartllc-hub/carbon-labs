"""Fix volume deal logic: tier free counts + avg-price eligibility for free vials."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

OLD = r"""function calcDeal(items){
  let units=[];
  items.forEach(i=>{for(let q=0;q<i.qty;q++)units.push({k:i.k,id:i.id,price:i.price});});
  units.sort((a,b)=>b.price-a.price);
  const tot=units.length;

  // Bac water deal: buy any 2 paid vials (non-bacwater), get 1 free bac water
  const paidVials=units.filter(u=>u.id!=='bacwater');
  const bacwaterInCart=items.find(i=>i.id==='bacwater');
  const bacwaterProd=PRODS.find(p=>p.id==='bacwater');
  let bacFree=false;
  if(paidVials.length>=2&&bacwaterProd){bacFree=true;}

  let fc=0;
  if(tot>=10)fc=4;else if(tot>=6)fc=2;else if(tot>=3)fc=1;
  if(!fc&&!bacFree)return{freeCount:0,savings:0,avgPaid:0,freeKeys:{},bacFree:false};
  const paid=units.slice(0,tot-fc),free=units.slice(tot-fc);
  const avg=paid.length?paid.reduce((s,u)=>s+u.price,0)/paid.length:0;
  let sav=0;
  const fk={};
  free.forEach(u=>{sav+=Math.min(u.price,avg);fk[u.k]=(fk[u.k]||0)+1;});
  if(bacFree&&bacwaterProd){
    const bwKey='bacwater_10mL';
    const bwPrice=bacwaterProd.sizes[0].p;
    if(!bacwaterInCart){sav+=bwPrice;}
    fk[bwKey]=(fk[bwKey]||0)+1;
  }
  return{freeCount:fc+(bacFree?1:0),savings:sav,avgPaid:avg,freeKeys:fk,bacFree};
}"""

NEW = r"""function calcDeal(items){
  const DEAL_TIERS=[{n:3,f:1},{n:6,f:2},{n:10,f:4}];
  const peptideUnits=[];
  items.forEach(i=>{
    if(i.id==='bacwater')return;
    for(let q=0;q<i.qty;q++)peptideUnits.push({k:i.k,id:i.id,price:i.price});
  });
  const n=peptideUnits.length;
  let fc=0;
  for(const t of DEAL_TIERS)if(n>=t.n)fc=t.f;

  const bacwaterInCart=items.find(i=>i.id==='bacwater');
  const bacwaterProd=PRODS.find(p=>p.id==='bacwater');
  const bacFree=n>=2&&!!bacwaterProd;
  if(!fc&&!bacFree)return{freeCount:0,savings:0,avgPaid:0,freeKeys:{},bacFree:false,volFree:0};

  let free=[],paid=[...peptideUnits];
  if(fc>0){
    let pool=[...peptideUnits].sort((a,b)=>a.price-b.price);
    let slots=fc;
    while(slots>0&&pool.length>1){
      const candidate=pool[0];
      const rest=pool.slice(1);
      const avg=rest.reduce((s,u)=>s+u.price,0)/rest.length;
      if(candidate.price<=avg){
        free.push(candidate);
        pool=rest;
        slots--;
      }else break;
    }
    paid=pool;
  }
  const avgPaid=paid.length?paid.reduce((s,u)=>s+u.price,0)/paid.length:0;
  let sav=0,volFree=0;
  const fk={};
  free.forEach(u=>{
    if(u.price<=avgPaid){
      sav+=Math.min(u.price,avgPaid);
      fk[u.k]=(fk[u.k]||0)+1;
      volFree++;
    }
  });
  if(bacFree&&bacwaterProd){
    const bwKey='bacwater_10mL';
    const bwPrice=bacwaterProd.sizes[0].p;
    if(!bacwaterInCart)sav+=bwPrice;
    fk[bwKey]=(fk[bwKey]||0)+1;
  }
  return{freeCount:volFree+(bacFree?1:0),savings:sav,avgPaid,freeKeys:fk,bacFree,volFree};
}"""

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("calcDeal updated")
elif "DEAL_TIERS" in text:
    print("calcDeal already updated")
else:
    raise SystemExit("calcDeal block not found")

# Clarify promo copy for volume deals
OLD_PROMO_TEXT = (
    "const text=away===1?`You're 1 vial away from ${next.l} — add 1 more for ${next.f} free vial${next.f>1?'s':''}!`"
    ":`Add ${away} more vial${away>1?'s':''} to unlock ${next.l} (${next.f} free).`;"
)
NEW_PROMO_TEXT = (
    "const text=away===1?`You're 1 vial away from ${next.l} — add 1 more for ${next.f} free vial${next.f>1?'s':''}!`"
    ":`Add ${away} more vial${away>1?'s':''} to unlock ${next.l} (${next.f} free). Lowest-priced vials free, each up to your order avg.`;"
)
if OLD_PROMO_TEXT in text:
    text = text.replace(OLD_PROMO_TEXT, NEW_PROMO_TEXT, 1)
    print("promo text updated")

OLD_FAQ = "Buy 3 get 1 free, buy 6 get 2 free, buy 10 get 4 free. Free vials are the lowest-priced in your order, each capped at the average price of paid vials. Also: buy any 2 vials and receive a free 10mL bacteriostatic water."
NEW_FAQ = "Buy 3 get 1 free, buy 6 get 2 free, buy 10 get 4 free. Free vials are always the lowest-priced in your order and only apply when their price is at or below the average cost of your paid vials (savings capped at that average per free vial). Also: buy any 2 vials and receive a free 10mL bacteriostatic water."
if OLD_FAQ in text:
    text = text.replace(OLD_FAQ, NEW_FAQ, 1)
    print("FAQ updated")

OLD_VOLFREE = "const volFree=Math.max(0,deal.freeCount-(deal.bacFree?1:0));"
NEW_VOLFREE = "const volFree=deal.volFree!=null?deal.volFree:Math.max(0,deal.freeCount-(deal.bacFree?1:0));"
if OLD_VOLFREE in text:
    text = text.replace(OLD_VOLFREE, NEW_VOLFREE, 1)
    print("volFree helper updated")

p.write_text(text, encoding="utf-8")
print("done")
