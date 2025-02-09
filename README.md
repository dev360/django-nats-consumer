# django-nats-consumer
NATS + Django = ⚡️

## Installation

Please pay attention to the development status; this is Pre-Alpha software; expect the api to evolve as I start using this more in production.

```bash
pip install django-nats-consumer
```


## Usage

**settings.py**
```python
INSTALLED_APPS = [
    ...
    "nats_consumer",
]

NATS_CONSUMER = {
    "connect_args": {
        "servers": ["nats://localhost:4222"],
        "allow_reconnect": True,
        "max_reconnect_attempts": 5,
        "reconnect_time_wait": 1,
        "connect_timeout": 10,
    },
}
```

**{app_name}/consumers.py**
```python
# Consumers need to be in the consumers module in order to be loaded,
# or you can import them to force them to be loaded.
from nats_consumer import JetstreamPushConsumer

import logging

from nats_consumer import JetstreamPushConsumer, operations

logger = logging.getLogger(__name__)


class OrderConsumer(JetstreamPushConsumer):
    stream_name = "orders"
    subjects = [
        "orders.created",
    ]

    # You need to setup the streams
    async def setup(self):
        return [
            operations.CreateStream(
                name=self.stream_name,
                subjects=self.subjects,
                storage="file"
            ),
        ]

    async def handle_message(self, message):
        # The message only shows if its logged as error
        logger.error(f"Received message: {message.data}")

```

**publish.py**
```python
import asyncio

from nats_consumer import get_nats_client

async def publish_messages():
    ns = await get_nats_client()
    js = ns.jetstream()
    for i in range(5):
        data = {"id": i, "name": f"Order {i}"}
        data_b = json.dumps(data).encode("utf-8")
        print(f"Publishing message {i}...")
        await js.publish("orders.created", data_b)

if __name__ == "__main__":
    asyncio.run(publish_messages())

```

## Running Consumers
**To run a single consumer:**
```bash
python manage.py nats_consumer OrderConsumer --setup
```

**To run multiple consumers:**
```bash
python manage.py nats_consumer OrderConsumer AnotherConsumer
```

**To run all consumers:**
```bash
python manage.py nats_consumer
```

**Additional Options:**
```bash
# Enable uvloop for better performance
python manage.py nats_consumer --uvloop

# Enable auto-reload for development (watches for file changes)
python manage.py nats_consumer --reload

# Combine options
python manage.py nats_consumer OrderConsumer --uvloop --reload
```

**Note**
When running your code in production, uvloop typically provides better performance than the default asyncio event loop, but it's only available on Unix-like systems (Linux, macOS). To use uvloop, please install using:

```bash
pip install django-nats-consumer[uvloop]
```

And add the following to your settings.py:
```python
NATS_CONSUMER = {
    "event_loop_policy": "uvloop.EventLoopPolicy",
    ...
}
```

