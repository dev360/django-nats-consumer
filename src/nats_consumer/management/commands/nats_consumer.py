import asyncio
import logging
import logging.config
import os
import sys
import threading
from django.core.management.base import BaseCommand
from django.conf import settings
from nats_consumer.consumer import NatsConsumer
from nats_consumer.settings import config

if settings.DEBUG:
    from watchfiles import watch

logger = logging.getLogger(__name__)


def set_event_loop_policy():
    event_loop_policy_str = config.get("event_loop_policy")

    if event_loop_policy_str:
        try:
            # Dynamically evaluate the event loop policy string
            event_loop_policy = eval(event_loop_policy_str)
            asyncio.set_event_loop_policy(event_loop_policy)
            logger.info(f"Using {event_loop_policy_str} as the event loop policy.")
        except (ImportError, NameError, SyntaxError) as e:
            logger.error(f"Failed to set event loop policy: {e}")
            raise


class Command(BaseCommand):
    help = "Run NATS Consumers"

    def add_arguments(self, parser):
        parser.add_argument("consumer", type=str, nargs="*", help="Consumer name")
        parser.add_argument(
            "--log-level",
            type=str,
            choices=["ERROR", "WARNING", "INFO", "DEBUG"],
            default="INFO",
            help="Log level: ERROR, WARNING, INFO, DEBUG",
        )
        parser.add_argument("--setup", action="store_true", help="Setup the stream before running the consumer")
        parser.add_argument("--reload", action="store_true", help="Reload on code changes")

    def handle(self, *args, **options):
        set_event_loop_policy()
        reload = options.get("reload")
        if settings.DEBUG and reload:
            self.start_reloader()
        elif not settings.DEBUG and reload:
            logger.warning("Reload is not supported when DEBUG is false")
            return

        try:
            self.start_consumers(*args, **options)
        except KeyboardInterrupt:
            self.stop_reloader()
            logger.info("Consumer interrupted by user. Exiting...")

    def start_consumers(self, *args, **options):
        asyncio.run(self._handle(*args, **options))

    def start_reloader(self):
        self.stop_event = threading.Event()

        def watch_files():
            logger.info("Starting file watcher for reload...")
            for changes in watch(".", stop_event=self.stop_event):
                logger.info("Detected file change, reloading...")
                logger.debug(f"  Changes: {changes}")
                os.execv(sys.executable, ["python"] + sys.argv)

        # Start the file-watching in a separate thread
        self.watcher_thread = threading.Thread(target=watch_files, daemon=True)
        self.watcher_thread.start()

    def stop_reloader(self):
        if hasattr(self, "stop_event"):
            self.stop_event.set()  # Signal the thread to stop
        if hasattr(self, "watcher_thread"):
            self.watcher_thread.join()  # Wait for the thread to finish

    async def _handle(self, *args, **options):
        consumer_names = options["consumer"]
        if not consumer_names:
            consumer_names = None

        consumer_runs = [self.run_consumer(Consumer, options) for Consumer in NatsConsumer.filter(consumer_names)]
        await asyncio.gather(*consumer_runs)

    async def run_consumer(self, Consumer, options):
        if options["setup"]:
            operations = await Consumer().setup()
            for op in operations:
                await op.execute()

        while True:
            try:
                consumer = Consumer()
                await consumer.run()
            except Exception as e:
                logger.error(f"Consumer {Consumer.consumer_name} stopped with error: {e}")
            finally:
                if consumer.is_running:
                    await consumer.stop()
                logger.info(f"Restarting consumer {Consumer.consumer_name}...")
                await asyncio.sleep(1)  # Wait before restarting
