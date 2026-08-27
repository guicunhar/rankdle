from app.services.scoring import direction_for_guess, score_for_guess


def test_exact_guess_scores_100():
    assert score_for_guess(34, 34) == 100


def test_score_decreases_by_one_per_position():
    assert score_for_guess(12, 5) == 93  # matches the example from the product spec
    assert score_for_guess(40, 34) == 94
    assert score_for_guess(34, 40) == 94


def test_score_floors_at_zero():
    assert score_for_guess(200, 1) == 0
    assert score_for_guess(1, 200) == 0


def test_direction_for_guess():
    assert direction_for_guess(34, 34) == "correct"
    assert direction_for_guess(10, 34) == "lower"
    assert direction_for_guess(50, 34) == "higher"
