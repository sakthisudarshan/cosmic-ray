import pytest

from testable_demo.order_validator import validate_order, validate_quantity


class TestValidateQuantity:
    @pytest.mark.parametrize("quantity", [0, -1, -10])
    def test_non_positive_rejected(self, quantity):
        assert validate_quantity(quantity) is False

    @pytest.mark.parametrize("quantity", [101, 150])
    def test_over_limit_rejected(self, quantity):
        assert validate_quantity(quantity) is False

    @pytest.mark.parametrize("quantity", [1, 50, 100])
    def test_valid_quantities(self, quantity):
        assert validate_quantity(quantity) is True


class TestValidateOrder:
    def test_negative_total_rejected(self):
        assert validate_order(-1, 1, False) == "rejected"

    def test_zero_items_rejected(self):
        assert validate_order(10, 0, False) == "rejected"

    def test_zero_total_with_items_rejected(self):
        assert validate_order(0, 2, False) == "rejected"

    def test_member_high_total(self):
        assert validate_order(50, 1, True) == "approved_with_discount"

    def test_member_low_total(self):
        assert validate_order(49.99, 1, True) == "approved_member"

    def test_non_member_high_total(self):
        assert validate_order(100, 1, False) == "approved_standard"

    def test_non_member_low_total(self):
        assert validate_order(99.99, 1, False) == "pending_review"
