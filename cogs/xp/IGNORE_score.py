def calculate_score(
    levels: int,
    choomah_coins: int,
    bumps: int,
    level_multiplier: float,
    choomah_coin_multiplier: float,
    bumps_multiplier: float,
) -> float:
    """
    Calculates the score of a user based of their levels, coins, and how many times they've bumped.
    """
    return round(
        (
            (levels * level_multiplier)
            + (choomah_coins * choomah_coin_multiplier)
            + (bumps * bumps_multiplier)
        ),
        2,
    )
