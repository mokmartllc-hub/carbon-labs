"""Add DSIP and Melanotan II category filters to shop page."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

text = text.replace(
    "{id:'dsip',name:'DSIP',cat:'Other Research',tag:'Sleep Research Peptide',",
    "{id:'dsip',name:'DSIP',cat:'DSIP',tag:'Sleep Research Peptide',",
    1,
)
text = text.replace(
    "{id:'melanotan',name:'Melanotan II',cat:'Other Research',tag:'Melanocortin Research Peptide',",
    "{id:'melanotan',name:'Melanotan II',cat:'Melanotan II',tag:'Melanocortin Research Peptide',",
    1,
)
text = text.replace(
    "const CATS=['All','Metabolic Research','GH Research','Tissue Repair','Cellular Research','Neuro Research','Blends','Accessories'];",
    "const CATS=['All','Metabolic Research','GH Research','Tissue Repair','Cellular Research','Neuro Research','Blends','DSIP','Melanotan II','Accessories'];",
    1,
)

p.write_text(text, encoding="utf-8")
print("added DSIP and Melanotan II filters")
