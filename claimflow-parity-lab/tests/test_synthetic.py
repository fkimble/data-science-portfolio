from __future__ import annotations

import unittest

from claimflow.synthetic import GeneratorConfig, generate_claimflows
from claimflow.validate import validate_claimflows


class SyntheticTests(unittest.TestCase):
    def test_generator_is_deterministic(self) -> None:
        config = GeneratorConfig(patients=100, days=30, seed=123)
        left = generate_claimflows(config)
        right = generate_claimflows(config)
        self.assertEqual(left.to_csv(index=False), right.to_csv(index=False))

    def test_generated_data_validates(self) -> None:
        df = generate_claimflows(GeneratorConfig(patients=250, days=45, seed=5))
        self.assertTrue(validate_claimflows(df).passed)


if __name__ == "__main__":
    unittest.main()
