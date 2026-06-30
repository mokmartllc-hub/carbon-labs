"""Point GLP-3 RT 5mg/10mg at new product photos in public/images/."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

old = (
    "sizes:[{l:'5mg',p:20,img:IMGS.glp3_5,batch:'RT5-01'},{l:'10mg',p:35,img:IMGS.glp3_10,batch:'RT10-01'}"
    ",{l:'20mg',p:65,img:IMGS.glp3_20,batch:'RT20-01'}]"
)
new = (
    "sizes:[{l:'5mg',p:20,img:'/images/glp3-5mg.png',batch:'RT5-01'},{l:'10mg',p:35,img:'/images/glp3-10mg.png',batch:'RT10-01'}"
    ",{l:'20mg',p:65,img:IMGS.glp3_20,batch:'RT20-01'}]"
)

if new not in text:
    if old not in text:
        raise SystemExit("glp3rt sizes block not found")
    text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("updated glp3rt images")
