from src.validate_data import calculate_turnover_rate


def test_turnover_uses_average_headcount_not_ending_headcount_only():
    rate = calculate_turnover_rate(beginning_headcount=80, ending_headcount=100, terminations=9)

    assert rate == 0.1


def test_turnover_returns_zero_when_average_headcount_is_zero():
    assert calculate_turnover_rate(0, 0, 5) == 0
