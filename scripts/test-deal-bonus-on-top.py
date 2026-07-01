"""Verify volume deals add bonus vials on top, not discount cart items."""
from pathlib import Path

DEAL_TIERS = [(3, 1), (6, 2), (10, 4)]


def calc_deal(units):
    """units: list of prices for peptide vials in cart."""
    n = len(units)
    fc = 0
    for tier_n, tier_f in DEAL_TIERS:
        if n >= tier_n:
            fc = tier_f
    if not fc:
        return {"vol_free": 0, "savings": 0, "avg_paid": 0, "all_paid": n}

    avg_paid = sum(units) / n
    cheapest = min(units)
    vol_free = 0
    sav = 0.0
    for _ in range(fc):
        if cheapest <= avg_paid:
            sav += min(cheapest, avg_paid)
            vol_free += 1
    return {"vol_free": vol_free, "savings": sav, "avg_paid": avg_paid, "all_paid": n}


def test_six_same_price():
    d = calc_deal([40, 40, 40, 40, 40, 40])
    assert d["all_paid"] == 6, "all 6 vials stay paid"
    assert d["vol_free"] == 2, "6 paid -> 2 bonus on top"
    assert d["savings"] == 80.0, "2 bonus at $40 each"


def test_three_same_price():
    d = calc_deal([40, 40, 40])
    assert d["all_paid"] == 3
    assert d["vol_free"] == 1
    assert d["savings"] == 40.0


def test_two_no_deal():
    d = calc_deal([40, 40])
    assert d["vol_free"] == 0
    assert d["savings"] == 0.0


def test_mixed_prices():
    # 4x40 + 2x30 = 6 vials, bonus = 2x cheapest ($30)
    d = calc_deal([40, 40, 40, 40, 30, 30])
    assert d["vol_free"] == 2
    assert d["savings"] == 60.0


test_six_same_price()
test_three_same_price()
test_two_no_deal()
test_mixed_prices()
print("PASS bonus-on-top deal logic")
