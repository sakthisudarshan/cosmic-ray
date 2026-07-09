import pytest

from testable_demo.discount import apply_percentage_discount, tiered_shipping


class TestApplyPercentageDiscount:
    def test_no_discount(self):
        assert apply_percentage_discount(100, 0) == 100

    def test_full_discount(self):
        assert apply_percentage_discount(100, 100) == 0.0

    def test_half_discount(self):
        assert apply_percentage_discount(80, 50) == 40.0

    def test_third_discount_uses_true_division(self):
        assert apply_percentage_discount(100, 33) == 67.0

    def test_fractional_percent_uses_true_division(self):
        assert apply_percentage_discount(100, 33.7) == pytest.approx(66.3)

    def test_fractional_discount(self):
        assert apply_percentage_discount(200, 12.5) == 175.0

    def test_over_cap_percent_cannot_go_negative(self):
        assert apply_percentage_discount(100, 101) == 0.0

    def test_result_never_negative(self):
        assert apply_percentage_discount(10, 200) == 0.0

    def test_percent_just_below_floor(self):
        assert apply_percentage_discount(80, -0.01) == 80.0

    def test_percent_just_above_ceiling(self):
        assert apply_percentage_discount(80, 100.01) == 0.0

    def test_percent_at_ceiling_minus_epsilon(self):
        assert apply_percentage_discount(100, 99.99) == pytest.approx(0.01)

    def test_negative_percent_clamped(self):
        assert apply_percentage_discount(50, -10) == 50

    def test_over_100_percent_clamped(self):
        assert apply_percentage_discount(50, 150) == 0.0

    def test_101_percent_clamped(self):
        assert apply_percentage_discount(100, 101) == 0.0

    def test_percent_exactly_100(self):
        assert apply_percentage_discount(75, 100) == 0.0

    def test_small_positive_discount(self):
        assert apply_percentage_discount(200, 1) == 198.0

    def test_discount_never_returns_negative_literal(self):
        result = apply_percentage_discount(10, 100)
        assert result == 0.0
        assert result != 1.0
        assert result != -1.0


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
