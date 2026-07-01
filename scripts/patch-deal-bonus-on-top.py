"""Volume deals: bonus vials are added on top of paid cart qty, not discounted from cart."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"
text = p.read_text(encoding="utf-8")
before = len(text)

OLD_CALC = """  if(!fc&&!bacFree)return{freeCount:0,savings:0,avgPaid:0,freeKeys:{},bacFree:false,volFree:0};

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
  return{freeCount:volFree+(bacFree?1:0),savings:sav,avgPaid,freeKeys:fk,bacFree,volFree};"""

NEW_CALC = """  if(!fc&&!bacFree)return{freeCount:0,savings:0,avgPaid:0,freeKeys:{},bonusKeys:{},bacFree:false,volFree:0};

  const avgPaid=n?peptideUnits.reduce((s,u)=>s+u.price,0)/n:0;
  let sav=0,volFree=0;
  const fk={},bk={};
  if(fc>0&&n>0){
    const cheapest=peptideUnits.reduce((a,b)=>a.price<=b.price?a:b);
    for(let i=0;i<fc;i++){
      if(cheapest.price<=avgPaid){
        sav+=Math.min(cheapest.price,avgPaid);
        bk[cheapest.k]=(bk[cheapest.k]||0)+1;
        volFree++;
      }
    }
  }
  if(bacFree&&bacwaterProd){
    const bwKey='bacwater_10mL';
    const bwPrice=bacwaterProd.sizes[0].p;
    if(!bacwaterInCart)sav+=bwPrice;
    fk[bwKey]=(fk[bwKey]||0)+1;
  }
  return{freeCount:volFree+(bacFree?1:0),savings:sav,avgPaid,freeKeys:fk,bonusKeys:bk,bacFree,volFree};"""

OLD_PROMO_MAX = "headline:volFree>0?`${volFree} free vial${volFree>1?'s':''} applied — $${volSav.toFixed(2)} off`:'Buy 10 Get 4 Free — maximum deal applied!',sub:'Buy 10 Get 4 Free — lowest-priced vials free'"
NEW_PROMO_MAX = "headline:volFree>0?`${volFree} bonus vial${volFree>1?'s':''} added on top — $${volSav.toFixed(2)} off`:'Buy 10 Get 4 Free — maximum deal applied!',sub:'Buy 10 Get 4 Free — 14 vials total (10 paid + 4 bonus)'"

OLD_PROMO_UNLOCKED = "headline=away===1?`${volFree} free applied · Add 1 more for ${next.f} more free vial${fs}!`:`${volFree} free applied — $${volSav.toFixed(2)} off · Add ${away} more for ${next.f} more free!`;\n      sub=`${cur.l} active · Next: ${next.l}`;"
NEW_PROMO_UNLOCKED = "headline=away===1?`${volFree} bonus vial${volFree>1?'s':''} added · Add 1 for ${next.f} more bonus!`:`${volFree} bonus vial${volFree>1?'s':''} added on top — Add ${away} more for ${next.f} more bonus!`;\n      sub=`${cur.l} — ${cur.n+cur.f} vials total · Next: ${next.l}`;"

OLD_FAQ = "Buy 3 get 1 free, buy 6 get 2 free, buy 10 get 4 free. Free vials are always the lowest-priced in your order and only apply when their price is at or below the average cost of your paid vials (savings capped at that average per free vial). Also: buy any 2 vials and receive a free 10mL bacteriostatic water."
NEW_FAQ = "Buy 3 get 1 free, buy 6 get 2 free, buy 10 get 4 free. Bonus vials are added on top of what you purchase (e.g. 6 paid = 8 total). Bonuses match your lowest-priced vial, capped at your order average per bonus vial. Also: buy any 2 vials and receive a free 10mL bacteriostatic water."

if OLD_CALC not in text:
    if "bonusKeys" in text and "bk[cheapest.k]" in text:
        print("calcDeal already patched")
    else:
        raise SystemExit("calcDeal block not found")

text = text.replace(OLD_CALC, NEW_CALC, 1)

if OLD_PROMO_MAX in text:
    text = text.replace(OLD_PROMO_MAX, NEW_PROMO_MAX, 1)
elif "bonus vial" in text and "added on top" in text:
    print("promo max already patched")
else:
    raise SystemExit("promo max block not found")

if OLD_PROMO_UNLOCKED in text:
    text = text.replace(OLD_PROMO_UNLOCKED, NEW_PROMO_UNLOCKED, 1)
elif "bonus vial" in text and "added · Add 1" in text:
    print("promo unlocked already patched")
else:
    raise SystemExit("promo unlocked block not found")

if OLD_FAQ in text:
    text = text.replace(OLD_FAQ, NEW_FAQ, 1)

if len(text) < 10_000_000 or not text.rstrip().endswith("</html>"):
    raise SystemExit(f"REFUSING TO WRITE: truncated ({len(text)} bytes)")

p.write_text(text, encoding="utf-8")
print(f"patched deal bonus-on-top: {before} -> {len(text)} bytes")
