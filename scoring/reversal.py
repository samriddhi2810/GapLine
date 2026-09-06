from __future__ import annotations

from .constants import REVERSAL_EXCURSION_MULTIPLIER, REVERSAL_RETURN_RATIO


def detect_reversal(max_excursion_return: float, final_return: float, expected_gap_volatility: float) -> bool:
    if expected_gap_volatility <= 0:
        return False
    far_enough = abs(max_excursion_return) >= REVERSAL_EXCURSION_MULTIPLIER * expected_gap_volatility
    returned_close = abs(final_return) <= REVERSAL_RETURN_RATIO * abs(max_excursion_return)
    return far_enough and returned_close
