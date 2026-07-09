"""Discount calculation with operator-sensitive comparisons."""


def apply_percentage_discount(price: float, percent: float) -> float:
    """Apply a percentage discount and never return a negative price."""
    if percent < 0:
        percent = 0
    if percent > 100:
        percent = 100
    discounted = price - (price * percent / 100)
    if discounted < 0:
        return 0.0
    return discounted


def tiered_shipping(weight_kg: float) -> float:
    """Return shipping cost based on weight boundaries."""
    if weight_kg <= 0:
        return 0.0
    if weight_kg <= 5:
        return 5.0
    if weight_kg <= 20:
        return 12.0
    return 25.0
