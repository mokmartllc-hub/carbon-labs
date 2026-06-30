"""Move DSIP and Melanotan II into Other Research category."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

replacements = [
    ("{id:'dsip',name:'DSIP',cat:'DSIP',tag:", "{id:'dsip',name:'DSIP',cat:'Other Research',tag:"),
    ("{id:'melanotan',name:'Melanotan II',cat:'Melanotan II',tag:", "{id:'melanotan',name:'Melanotan II',cat:'Other Research',tag:"),
    (
        "const CATS=['All','Metabolic Research','GH Research','Tissue Repair','Cellular Research','Neuro Research','Blends','DSIP','Melanotan II','Accessories'];",
        "const CATS=['All','Metabolic Research','GH Research','Tissue Repair','Cellular Research','Neuro Research','Blends','Other Research','Accessories'];",
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
        print("replaced:", old[:50])
    elif new.split("'")[1] in text and "Other Research" in new:
        print("already:", old[:40])

p.write_text(text, encoding="utf-8")
print("done")
