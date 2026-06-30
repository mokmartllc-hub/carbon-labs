import pathlib

t = pathlib.Path(__file__).resolve().parent.parent / "public" / "index.html"
text = t.read_text(encoding="utf-8")
checks = {
    "size ok": len(text) > 30_000_000,
    "account page": "paccount" in text,
    "orders page": "porders" in text,
    "go pages": "account','orders" in text,
    "api.js": "/api.js" in text,
    "function go": "function go" in text,
    "ends ok": text.strip().endswith("</html>"),
}
for k, v in checks.items():
    print(k, v)
