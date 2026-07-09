import pytest

from testable_demo.discount import apply_percentage_discount, tiered_shipping


class TestApplyPercentageDiscount:
    def test_no_discount(self):
        assert apply_percentage_discount(100, 0) == 100

    def test_full_discount(self):
        assert apply_percentage_discount(100, 100) == 0.0

    def test_half_discount(self):
        assert apply_percentage_discount(80, 50) == 40.0

    def test_negative_percent_clamped(self):
        assert apply_percentage_discount(50, -10) == 50

    def test_over_100_percent_clamped(self):
        assert apply_percentage_discount(50, 150) == 0.0


class TestTieredShipping:
    @pytest.mark.parametrize(
        "weight,expected",
        [
            (0, 0.0),
            (-1, 0.0),
            (1, 5.0),
            (5, 5.0),
            (5.01, 12.0),
            (20, 12.0),
            (20.01, 25.0),
            (100, 25.0),
        ],
    )
    def test_weight_boundaries(self, weight, expected):
        assert tiered_shipping(weight) == expected
