def score_for_guess(rank_guessed: int, target_rank: int) -> int:
    """100 if exact, minus 1 per position of difference, floored at 0."""
    diff = abs(rank_guessed - target_rank)
    return max(0, 100 - diff)


def direction_for_guess(rank_guessed: int, target_rank: int) -> str:
    if rank_guessed == target_rank:
        return "correct"
    return "lower" if rank_guessed < target_rank else "higher"
