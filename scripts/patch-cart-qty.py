"""Add cart quantity +/- controls to index.html."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

CSS = """
.qtystep{display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:3px 5px}
.qtystep-sm .qtybtn{width:28px;height:28px;font-size:16px;padding:0}
.qtystep-sm .qtyval{min-width:20px;text-align:center;font-size:12px;font-weight:800;color:white}
.qtystep-lg .qtybtn{width:36px;height:36px}
.qtystep-lg .qtyval{min-width:28px;text-align:center;font-size:15px;font-weight:800;color:white}
.cart-qtyrow{display:flex;align-items:center;justify-content:space-between;margin-top:8px;gap:10px}
.cart-qtyrow .cartprice{margin-top:0}
.atcbtn-alt{margin-top:10px;background:rgba(255,255,255,.08)!important;color:white;border:1px solid rgba(255,255,255,.15)!important}
"""

if ".qtystep{" not in text:
    text = text.replace(
        ".cartrm{font-size:11px;color:rgba(255,80,80,.55);cursor:pointer;margin-top:3px;display:inline-block}",
        ".cartrm{font-size:11px;color:rgba(255,80,80,.55);cursor:pointer;margin-top:3px;display:inline-block}"
        + CSS,
        1,
    )

OLD_PCARD = (
    "function pcard(p){\n"
    "  const sz=p.sizes[0],fr=p.sizes.length>1?'<span class=\"fr\">from</span>':'';\n"
    "  return`<div class=\"pc\" onclick=\"showProd('${p.id}')\"><div class=\"pimg\"><img src=\"${sz.img}\" alt=\"${p.name}\" loading=\"lazy\">${p.badge?`<div class=\"pbadge\">${p.badge}</div>`:''}</div><div class=\"pbody\"><h3>${p.name}</h3><div class=\"pcat\">${p.tag}</div><div class=\"pfoot\"><div class=\"pprice\">${fr}$${sz.p}.00</div><button class=\"badd\" onclick=\"event.stopPropagation();qadd('${p.id}')\">Add to cart</button></div></div></div>`;\n"
    "}"
)

NEW_PCARD = (
    "function escAttr(s){return String(s??'').replace(/&/g,'&amp;').replace(/\"/g,'&quot;').replace(/'/g,'&#39;');}\n"
    "function cartKey(p,sz){return p.id+'_'+sz.l;}\n"
    "function cartItemQty(k){const i=cart.find(x=>x.k===k);return i?i.qty:0;}\n"
    "function qtyStepperHtml(k,sm){const q=cartItemQty(k),cls=sm?'qtystep qtystep-sm':'qtystep qtystep-lg';return `<div class=\"${cls}\" onclick=\"event.stopPropagation()\"><button type=\"button\" class=\"qtybtn\" data-k=\"${escAttr(k)}\" onclick=\"setCartQtyByEl(this,-1)\">−</button><span class=\"qtyval\">${q}</span><button type=\"button\" class=\"qtybtn\" data-k=\"${escAttr(k)}\" onclick=\"setCartQtyByEl(this,1)\">+</button></div>`;}\n"
    "function cardAddHtml(p){const k=cartKey(p,p.sizes[0]);if(cartItemQty(k)>0)return qtyStepperHtml(k,true);return `<button class=\"badd\" onclick=\"event.stopPropagation();qadd('${p.id}')\">Add to cart</button>`;}\n"
    "function pcard(p){\n"
    "  const sz=p.sizes[0],fr=p.sizes.length>1?'<span class=\"fr\">from</span>':'';\n"
    "  return`<div class=\"pc\" data-pid=\"${p.id}\" onclick=\"showProd('${p.id}')\"><div class=\"pimg\"><img src=\"${sz.img}\" alt=\"${p.name}\" loading=\"lazy\">${p.badge?`<div class=\"pbadge\">${p.badge}</div>`:''}</div><div class=\"pbody\"><h3>${p.name}</h3><div class=\"pcat\">${p.tag}</div><div class=\"pfoot\"><div class=\"pprice\">${fr}$${sz.p}.00</div>${cardAddHtml(p)}</div></div></div>`;\n"
    "}"
)

if "function cardAddHtml" not in text and OLD_PCARD in text:
    text = text.replace(OLD_PCARD, NEW_PCARD, 1)

OLD_ATC = '        <button class="atcbtn" onclick="pdadd()">Add to Cart</button>'
NEW_ATC = '        <div id="pd-atc">${pdAtcInner()}</div>'
if NEW_ATC not in text and OLD_ATC in text:
    text = text.replace(OLD_ATC, NEW_ATC, 1)

OLD_SETSZ = "function setSz(i){aSz=i;const p=aProd,sz=p.sizes[i];document.getElementById('pdmainimg').src=sz.img;document.getElementById('pdprice').textContent='$'+sz.p+'.00';document.querySelectorAll('.szbtn').forEach((b,j)=>b.classList.toggle('active',j===i));document.querySelectorAll('.pdthumb').forEach((b,j)=>b.classList.toggle('active',j===i));const ssl=document.getElementById('szsel');if(ssl)ssl.textContent='— '+sz.l;const bs=document.getElementById('batchspan');if(bs)bs.textContent=sz.batch;}"
NEW_SETSZ = OLD_SETSZ.replace("if(bs)bs.textContent=sz.batch;", "if(bs)bs.textContent=sz.batch;updPdAtc();")
if "updPdAtc();" not in text and OLD_SETSZ in text:
    text = text.replace(OLD_SETSZ, NEW_SETSZ, 1)

OLD_ADD_BLOCK = (
    "function pdadd(){if(aProd)addC(aProd,aProd.sizes[aSz],aQty);}\n"
    "function qadd(id){const p=PRODS.find(x=>x.id===id);addC(p,p.sizes[0],1);}"
)

NEW_ADD_BLOCK = (
    "function pdAtcInner(){if(!aProd)return'';const k=cartKey(aProd,aProd.sizes[aSz]);if(cartItemQty(k)>0)return qtyStepperHtml(k,false)+'<button class=\"atcbtn atcbtn-alt\" onclick=\"openCart()\">View Cart →</button>';return `<button class=\"atcbtn\" onclick=\"pdadd()\">Add to Cart</button>`;}\n"
    "function updPdAtc(){const el=document.getElementById('pd-atc');if(el&&aProd)el.innerHTML=pdAtcInner();}\n"
    "function updCardBtns(){document.querySelectorAll('.pc[data-pid]').forEach(el=>{const p=PRODS.find(x=>x.id===el.dataset.pid);if(!p)return;const foot=el.querySelector('.pfoot');if(!foot)return;const fr=p.sizes.length>1?'<span class=\"fr\">from</span>':'';foot.innerHTML=`<div class=\"pprice\">${fr}$${p.sizes[0].p}.00</div>${cardAddHtml(p)}`;});}\n"
    "function setCartQtyByEl(el,delta){setCartQty(el.dataset.k,delta);}\n"
    "function setCartQty(k,delta){const ex=cart.find(i=>i.k===k);if(!ex)return;ex.qty+=delta;if(ex.qty<=0)cart=cart.filter(i=>i.k!==k);updCC();renderCart();updCardBtns();updPdAtc();}\n"
    "function pdadd(){if(aProd)addC(aProd,aProd.sizes[aSz],aQty);}\n"
    "function qadd(id){const p=PRODS.find(x=>x.id===id);addC(p,p.sizes[0],1);}"
)

if "function setCartQty" not in text and OLD_ADD_BLOCK in text:
    text = text.replace(OLD_ADD_BLOCK, NEW_ADD_BLOCK, 1)

OLD_ADDC = "function addC(p,sz,qty){const k=p.id+'_'+sz.l,ex=cart.find(i=>i.k===k);if(ex)ex.qty+=qty;else cart.push({k,id:p.id,name:p.name,size:sz.l,price:sz.p,img:sz.img,qty});updCC();renderCart();openCart();}"
NEW_ADDC = "function addC(p,sz,qty){const k=p.id+'_'+sz.l,ex=cart.find(i=>i.k===k);if(ex)ex.qty+=qty;else cart.push({k,id:p.id,name:p.name,size:sz.l,price:sz.p,img:sz.img,qty});updCC();renderCart();updCardBtns();updPdAtc();openCart();}"
if NEW_ADDC not in text and OLD_ADDC in text:
    text = text.replace(OLD_ADDC, NEW_ADDC, 1)

OLD_RMC = "function rmC(k){cart=cart.filter(i=>i.k!==k);updCC();renderCart();}"
NEW_RMC = "function rmC(k){cart=cart.filter(i=>i.k!==k);updCC();renderCart();updCardBtns();updPdAtc();}"
if "updCardBtns();updPdAtc();" not in text.split("function rmC")[1][:80] if "function rmC" in text else False:
    if OLD_RMC in text:
        text = text.replace(OLD_RMC, NEW_RMC, 1)

# Cart sidebar line - replace cart item template
OLD_CART_LINE = "<p>${i.size} · Qty ${i.qty}</p><div class=\"cartprice\">$${(i.price*i.qty).toFixed(2)}</div><span class=\"cartrm\" onclick=\"rmC('${i.k}')\">Remove</span>"
NEW_CART_LINE = "<p>${i.size}</p><div class=\"cart-qtyrow\"><div class=\"cartprice\">$${(i.price*i.qty).toFixed(2)}</div>${qtyStepperHtml(i.k,true)}</div>"

if NEW_CART_LINE not in text and OLD_CART_LINE in text:
    text = text.replace(OLD_CART_LINE, NEW_CART_LINE, 1)

p.write_text(text, encoding="utf-8")
print("cart qty patch applied, size", p.stat().st_size)
