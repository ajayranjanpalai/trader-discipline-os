import unittest

from routes.trades import _trade_fields


class TradePartialCloseTests(unittest.TestCase):
    def test_partial_close_derives_remaining_quantity(self):
        payload = {
            "pair": "BTC/USDT",
            "direction": "long",
            "entry": 100,
            "exit": 110,
            "stop_loss": 95,
            "position_size": 100,
            "closed_quantity": 40,
            "pnl": 400,
            "risk_reward": 2,
            "emotion": "calm",
        }

        fields = _trade_fields(payload)

        self.assertEqual(fields["closed_quantity"], 40.0)
        self.assertEqual(fields["remaining_quantity"], 60.0)

    def test_missing_closed_quantity_defaults_to_full_position(self):
        payload = {
            "pair": "BTC/USDT",
            "direction": "long",
            "entry": 100,
            "exit": 110,
            "stop_loss": 95,
            "position_size": 100,
            "pnl": 1000,
            "risk_reward": 2,
            "emotion": "calm",
        }

        fields = _trade_fields(payload)

        self.assertEqual(fields["closed_quantity"], 100.0)
        self.assertEqual(fields["remaining_quantity"], 0.0)


if __name__ == "__main__":
    unittest.main()
