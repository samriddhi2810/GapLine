import math
from django.test import SimpleTestCase

from scoring.divergence import benchmark_component_points, benchmark_divergence_ratio, calculate_residual_return
from scoring.engine import score_change
from scoring.volatility import calculate_returns, component_points, expected_gap_volatility, sample_standard_deviation


class ScoringMathTests(SimpleTestCase):
    def test_return_calculation(self):
        returns = calculate_returns([100, 110, 99])
        self.assertAlmostEqual(returns[0], 0.1)
        self.assertAlmostEqual(returns[1], -0.1)

    def test_sample_standard_deviation(self):
        self.assertAlmostEqual(sample_standard_deviation([1, 2, 3]), 1.0)

    def test_own_surprise(self):
        expected = expected_gap_volatility(0.02, 4)
        self.assertAlmostEqual(expected, 0.04)
        ratio = 0.08 / expected
        self.assertAlmostEqual(ratio, 2.0)
        self.assertAlmostEqual(component_points(ratio, 45, 3), 30.0)

    def test_benchmark_divergence(self):
        residual = calculate_residual_return(0.08, 0.02)
        self.assertAlmostEqual(residual, 0.06)
        ratio = benchmark_divergence_ratio(residual, 0.03)
        self.assertAlmostEqual(ratio, 2.0)
        self.assertAlmostEqual(benchmark_component_points(ratio), 36.666666666666664)

    def test_final_score(self):
        result = score_change(0.08, 0.02, 0.02, 0.015, 4, 0.08)
        self.assertEqual(result.attention_score, round(result.own_component_points + result.benchmark_component_points))
