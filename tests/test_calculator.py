import pytest

from testable_demo.calculator import clamp, classify_score, safe_divide


class TestClamp:
    def test_below_minimum(self):
        assert clamp(-5, 0, 10) == 0

    def test_above_maximum(self):
        assert clamp(15, 0, 10) == 10

    def test_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_at_boundaries(self):
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10


class TestSafeDivide:
    def test_normal_division(self):
        assert safe_divide(10, 2) == 5.0

    def test_zero_denominator(self):
        assert safe_divide(10, 0) == 0.0

    def test_negative_denominator(self):
        assert safe_divide(10, -2) == -5.0


class TestClassifyScore:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (-1, "invalid"),
            (0, "fail"),
            (49, "fail"),
            (50, "pass"),
            (69, "pass"),
            (70, "merit"),
            (89, "merit"),
            (90, "distinction"),
            (100, "distinction"),
        ],
    )
    def test_boundaries(self, score, expected):
        assert classify_score(score) == expected
