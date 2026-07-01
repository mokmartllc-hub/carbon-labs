"""Cart volume promo bar resets after each tier and progresses toward the next."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "public" / "index.html"
text = p.read_text(encoding="utf-8")
before = len(text)

OLD = """  if(paid>=10){
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
  if(bacProd){"""

NEW = """  const volFree=deal.volFree!=null?deal.volFree:Math.max(0,deal.freeCount-(deal.bacFree?1:0));
  const volSav=deal.savings||0;
  if(paid>=10){
    promos.push({kind:'volume',t:'active',badge:'VOLUME DEAL',status:'UNLOCKED',headline:volFree>0?`${volFree} free vial${volFree>1?'s':''} applied — $${volSav.toFixed(2)} off`:'Buy 10 Get 4 Free — maximum deal applied!',sub:'Buy 10 Get 4 Free — lowest-priced vials free',pct:100});
  }else if(next){
    const from=cur?cur.n:0;
    const away=next.n-paid;
    const pct=tierProgress(paid,from,next.n);
    const fs=next.f>1?'s':'';
    let headline,sub,status,t;
    if(cur&&volFree>0){
      status=away===1?'ALMOST THERE!':'UNLOCKED';
      t=away===1?'near':'progress';
      headline=away===1?`${volFree} free applied · Add 1 more for ${next.f} more free vial${fs}!`:`${volFree} free applied — $${volSav.toFixed(2)} off · Add ${away} more for ${next.f} more free!`;
      sub=`${cur.l} active · Next: ${next.l}`;
    }else{
      t=away===1?'near':'progress';
      status=away===1?'ALMOST THERE!':null;
      headline=away===1?`Add 1 more vial for ${next.f} FREE bonus vial${fs}!`:`Add ${away} more vials for ${next.f} FREE bonus vial${fs}!`;
      sub=`${next.l} — ${next.total} vials total`;
    }
    promos.push({kind:'volume',t,badge:'VOLUME DEAL',status,headline,sub,pct,cta:'Add another vial →',ctaFn:"closeCart();go('shop')"});
  }
  if(bacProd){"""

OLD_OVERRIDE = """  const volFree=deal.volFree!=null?deal.volFree:Math.max(0,deal.freeCount-(deal.bacFree?1:0));
  if(volFree>0&&deal.savings>0&&paid>=3){
    const vol=promos.find(p=>p.kind==='volume');
    if(vol&&vol.t!=='active'){
      vol.t='active';vol.status='APPLIED';vol.pct=100;
      vol.headline=`${volFree} free vial${volFree>1?'s':''} applied — $${deal.savings.toFixed(2)} off`;
      vol.sub='Lowest-priced vials free, each up to your order average';vol.cta=null;
    }
  }
  return promos;"""

NEW_RETURN = "  return promos;"

if OLD not in text:
    if "volFree applied · Add 1 more" in text:
        print("already patched")
    else:
        raise SystemExit("volume promo block not found")

text = text.replace(OLD, NEW, 1)

if OLD_OVERRIDE in text:
    text = text.replace(OLD_OVERRIDE, NEW_RETURN, 1)
elif "vol.status='APPLIED'" not in text:
    print("override removed ok")
else:
    raise SystemExit("override block not found")

if len(text) < 10_000_000 or not text.rstrip().endswith("</html>"):
    raise SystemExit(f"REFUSING TO WRITE: truncated ({len(text)} bytes)")

p.write_text(text, encoding="utf-8")
print(f"patched cart promo tiers: {before} -> {len(text)} bytes")
