"""Extract embedded catalog from index.html and upsert to Supabase via REST (service SQL)."""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "public" / "index.html"
CONFIG = ROOT / "public" / "config.js"

IMGS_KEYS = [
    "glp3_20", "bacwater", "bpc157", "dsip", "ghkcu", "glp1", "glow", "klow",
    "melanotan", "motsc", "nad500", "selank", "semax", "tesam", "wolverine",
]


def load_config():
    text = CONFIG.read_text(encoding="utf-8")
    url = re.search(r"window\.SUPABASE_URL\s*=\s*'([^']+)'", text).group(1)
    key = re.search(r"window\.SUPABASE_ANON_KEY\s*=\s*'([^']+)'", text).group(1)
    return url, key


def extract_quoted_value(text: str, key: str) -> str:
    marker = f'{key}:"'
    idx = text.find(marker)
    if idx == -1:
        raise KeyError(key)
    start = idx + len(marker)
    end = start
    while end < len(text):
        if text[end] == '"':
            break
        end += 1
    return text[start:end]


def parse_sizes(sizes_str: str, imgs: dict) -> list:
    sizes = []
    for m in re.finditer(
        r"\{l:'([^']+)',p:(\d+),img:(?:'([^']*)'|IMGS\.(\w+)),batch:'([^']*)'\}",
        sizes_str,
    ):
        l, p, url, img_key, batch = m.groups()
        img = url if url else imgs[img_key]
        sizes.append({
            "l": l,
            "p": int(p),
            "img": img,
            "batch": batch,
            "stock": 100,
        })
    return sizes


def parse_bullets(block: str) -> list:
    m = re.search(r"bullets:\[(.*?)\]", block, re.DOTALL)
    if not m:
        return []
    return re.findall(r"'((?:\\'|[^'])*)'", m.group(1))


def parse_products(text: str, imgs: dict) -> list:
    start = text.index("const PRODS_RAW=[")
    end = text.index("\n];", start)
    raw = text[start:end]
    chunks = re.split(r"\n  \{id:'", raw)
    products = []
    for chunk in chunks[1:]:
        block = "{id:'" + chunk
        pid = re.search(r"id:'([^']+)'", block).group(1)
        name = re.search(r"name:'([^']+)'", block).group(1)
        cat = re.search(r"cat:'([^']+)'", block).group(1)
        tag = re.search(r"tag:'([^']+)'", block).group(1)
        badge_m = re.search(r"badge:'([^']+)'", block)
        badge = badge_m.group(1) if badge_m else None
        exp = re.search(r"exp:'([^']+)'", block).group(1)
        desc = re.search(r"desc:'((?:\\'|[^'])*)'", block).group(1)
        storage = re.search(r"storage:'((?:\\'|[^'])*)'", block).group(1)
        sizes_m = re.search(r"sizes:\[(.*?)\],\s*exp:", block, re.DOTALL)
        sizes = parse_sizes(sizes_m.group(1), imgs)
        products.append({
            "id": pid,
            "name": name,
            "cat": cat,
            "tag": tag,
            "badge": badge,
            "exp": exp,
            "desc": desc,
            "bullets": parse_bullets(block),
            "storage": storage,
            "sizes": sizes,
            "active": True,
        })
    return products


def db_payload(p: dict, sort_order: int) -> dict:
    return {
        **p,
        "sort_order": sort_order,
        "updated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }


def upsert_via_rpc(url: str, key: str, products: list) -> None:
    admin_pass = "CarbonLabs2026!"
    for i, p in enumerate(products):
        payload = db_payload(p, i)
        body = json.dumps({"pass": admin_pass, "payload": payload}).encode("utf-8")
        req = urllib.request.Request(
            f"{url}/rest/v1/rpc/admin_upsert_product",
            data=body,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            if resp.status not in (200, 204):
                raise RuntimeError(f"Failed {p['id']}: {resp.status}")
        print(f"  synced {p['id']}")


def main():
    print("Reading index.html…")
    text = INDEX.read_text(encoding="utf-8")
    print("Extracting images…")
    imgs = {k: extract_quoted_value(text, k) for k in IMGS_KEYS}
    print("Parsing products…")
    products = parse_products(text, imgs)
    print(f"Found {len(products)} products")
    url, key = load_config()
    print("Upserting to Supabase…")
    upsert_via_rpc(url, key, products)
    print("Done.")


if __name__ == "__main__":
    main()
