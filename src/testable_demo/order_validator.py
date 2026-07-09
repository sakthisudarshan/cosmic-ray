"""Order validation with nested conditions and edge-case handling."""


def validate_quantity(quantity: int) -> bool:
    """Return True when quantity is within allowed purchase limits."""
    if quantity <= 0:
        return False
    if quantity > 100:
        return False
    return True


def validate_order(total: float, item_count: int, is_member: bool) -> str:
    """Validate an order and return approval status."""
    if total < 0:
        return "rejected"
    if item_count == 0:
        return "rejected"
    if total == 0 and item_count > 0:
        return "rejected"

    if is_member:
        if total >= 50:
            return "approved_with_discount"
        return "approved_member"

    if total >= 100:
        return "approved_standard"
    return "pending_review"
