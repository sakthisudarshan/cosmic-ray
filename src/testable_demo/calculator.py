"""Arithmetic helpers with boundary-sensitive logic."""


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Restrict value to the inclusive range [minimum, maximum]."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def safe_divide(numerator: float, denominator: float) -> float:
    """Divide two numbers, returning 0.0 when denominator is zero."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def classify_score(score: int) -> str:
    """Map numeric score to letter grade using boundary thresholds."""
    if score < 0:
        return "invalid"
    if score < 50:
        return "fail"
    if score < 70:
        return "pass"
    if score < 90:
        return "merit"
    return "distinction"
