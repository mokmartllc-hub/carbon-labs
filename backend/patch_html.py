from pathlib import Path

p = Path(__file__).resolve().parent.parent / "public" / "index.html"
text = p.read_text(encoding="utf-8")

replacements = [
    (
        '<input type="email" placeholder="Enter your email"><button>Subscribe</button>',
        '<input type="email" id="nl-email" placeholder="Enter your email"><button id="nl-btn" onclick="subscribeNewsletter()">Subscribe</button>',
    ),
    (
        '<input type="text" placeholder="Your name" class="cf-input">',
        '<input type="text" id="cf-name" placeholder="Your name" class="cf-input">',
    ),
    (
        '<input type="email" placeholder="your@email.com" class="cf-input">',
        '<input type="email" id="cf-email" placeholder="your@email.com" class="cf-input">',
    ),
    (
        '<input type="text" placeholder="AL-00000" class="cf-input">',
        '<input type="text" id="cf-order" placeholder="AL-00000" class="cf-input">',
    ),
    (
        '<select class="cf-input cf-select">',
        '<select id="cf-subject" class="cf-input cf-select">',
    ),
    (
        '<textarea class="cf-input cf-textarea" placeholder="Tell us how we can help…"></textarea>',
        '<textarea id="cf-message" class="cf-input cf-textarea" placeholder="Tell us how we can help…"></textarea>',
    ),
    (
        "renderCart();\n</script>\n</body></html>",
        'renderCart();\n</script>\n<script src="/api.js"></script>\n</body></html>',
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"MISSING: {old[:80]!r}")
    text = text.replace(old, new, 1)
    print("patched:", old[:50])

p.write_text(text, encoding="utf-8")
print("done", len(text))
