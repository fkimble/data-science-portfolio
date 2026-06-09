from __future__ import annotations

import unittest

from careroute.synthetic import GeneratorConfig, generate_referrals
from careroute.validate import validate_referrals


class SyntheticTests(unittest.TestCase):
    def test_generator_is_deterministic(self) -> None:
        config = GeneratorConfig(referrals=120, days=30, seed=11)
        left = generate_referrals(config)
        right = generate_referrals(config)
        self.assertEqual(left.to_csv(index=False), right.to_csv(index=False))

    def test_generated_data_validates(self) -> None:
        df = generate_referrals(GeneratorConfig(referrals=300, days=60, seed=3))
        self.assertTrue(validate_referrals(df).passed)


if __name__ == "__main__":
    unittest.main()
