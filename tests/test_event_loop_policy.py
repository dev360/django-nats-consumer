import unittest
from unittest.mock import MagicMock, patch

from nats_consumer.management.commands.nats_consumer import set_event_loop_policy
from nats_consumer.settings import config


class TestEventLoopPolicy(unittest.TestCase):
    @patch("asyncio.set_event_loop_policy")
    def test_no_op_when_no_policy_set(self, mock_set_event_loop_policy):
        # Ensure no event loop policy is set
        with patch.dict(config, {"event_loop_policy": None}):
            set_event_loop_policy()
            mock_set_event_loop_policy.assert_not_called()

    @patch("asyncio.set_event_loop_policy")
    def test_set_uvloop_policy(self, mock_set_event_loop_policy):
        # Set the event loop policy to uvloop
        with patch.dict(config, {"event_loop_policy": "uvloop.EventLoopPolicy"}):
            with patch("uvloop.EventLoopPolicy", MagicMock()) as mock_policy:
                set_event_loop_policy()
                mock_set_event_loop_policy.assert_called_once()
                mock_policy.assert_called_once()  # Ensure the policy is instantiated

    @patch("asyncio.set_event_loop_policy")
    def test_invalid_policy_raises_error(self, mock_set_event_loop_policy):
        # Set an invalid event loop policy
        with patch.dict(config, {"event_loop_policy": "nonexistent.Policy"}):
            with self.assertRaises(ModuleNotFoundError):
                set_event_loop_policy()


if __name__ == "__main__":
    unittest.main()
