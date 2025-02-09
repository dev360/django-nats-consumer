import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from django.conf import settings
from src.nats_consumer.management.commands.nats_consumer import Command
import asyncio


class TestReloadFunctionality(unittest.TestCase):
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.stop_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_consumers", new_callable=MagicMock)
    def test_reload_calls_start_reloader(self, mock_start_consumers, mock_stop_reloader, mock_start_reloader):
        # Set DEBUG to True for this test
        with patch.object(settings, "DEBUG", True):
            command = Command()
            options = {"reload": True}

            # Run the handle method
            command.handle(**options)

            # Assert start_reloader is called
            mock_start_reloader.assert_called_once()
            # Assert start_consumers is called
            mock_start_consumers.assert_called_once()

    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.stop_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_consumers", new_callable=MagicMock)
    def test_keyboard_interrupt_calls_stop_reloader(
        self, mock_start_consumers, mock_stop_reloader, mock_start_reloader
    ):
        # Set DEBUG to True for this test
        with patch.object(settings, "DEBUG", True):
            command = Command()
            options = {"reload": True}

            # Simulate KeyboardInterrupt
            mock_start_consumers.side_effect = KeyboardInterrupt

            # Run the handle method
            try:
                command.handle(**options)
            except KeyboardInterrupt:
                pass

            # Assert stop_reloader is called
            mock_stop_reloader.assert_called_once()

    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.stop_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_consumers", new_callable=MagicMock)
    def test_no_start_reloader_when_debug_false(self, mock_start_consumers, mock_stop_reloader, mock_start_reloader):
        # Set DEBUG to False for this test
        with patch.object(settings, "DEBUG", False):
            command = Command()
            options = {"reload": True}

            # Run the handle method
            command.handle(**options)

            # Assert start_reloader is not called
            mock_start_reloader.assert_not_called()

    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.stop_reloader")
    @patch("src.nats_consumer.management.commands.nats_consumer.Command.start_consumers", new_callable=MagicMock)
    def test_no_start_reloader_when_no_reload_flag(self, mock_start_consumers, mock_stop_reloader, mock_start_reloader):
        # Set DEBUG to True for this test
        with patch.object(settings, "DEBUG", True):
            command = Command()
            options = {"reload": False}

            # Run the handle method
            command.handle(**options)

            # Assert start_reloader is not called
            mock_start_reloader.assert_not_called()


if __name__ == "__main__":
    unittest.main()
