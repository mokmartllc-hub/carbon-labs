"""Quick sanity check for tiered cart promo progress bars."""
from pathlib import Path

# Minimal JS logic extracted for testing in Python
DEAL_TIERS = [(3, 1), (6, 2), (10, 4)]
tiers = [
    {"n": 3, "f": 1, "l": "Buy 3 Get 1 Free"},
    {"n": 6, "f": 2, "l": "Buy 6 Get 2 Free"},
    {"n": 10, "f": 4, "l": "Buy 10 Get 4 Free"},
]


def tier_progress(paid, from_n, goal):
    if goal <= from_n:
        return 100
    return min(100, max(0, ((paid - from_n) / (goal - from_n)) * 100))


def promo_pct(paid):
    cur = next_t = None
    for tier in tiers:
        if paid >= tier["n"]:
            cur = tier
        elif not next_t:
            next_t = tier
            break
    if paid >= 10:
        return 100
    if not next_t:
        return 100
    from_n = cur["n"] if cur else 0
    return round(tier_progress(paid, from_n, next_t["n"]))


cases = [
    (1, 33),
    (2, 67),
    (3, 0),  # reset after tier 1
    (4, 33),
    (5, 67),
    (6, 0),  # reset after tier 2
    (8, 50),
    (9, 75),
    (10, 100),
]
failed = []
for paid, expected in cases:
    got = promo_pct(paid)
    if got != expected:
        failed.append((paid, expected, got))

if failed:
    for row in failed:
        print("FAIL", row)
    raise SystemExit(1)
print("PASS tier progress:", cases)
