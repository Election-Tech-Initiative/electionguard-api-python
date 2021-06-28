from typing import Iterable, Any, Protocol
from queue import SimpleQueue

import sys
import pika

from .settings import Settings, QueueMode

__all__ = [
    "IMessageQueue",
    "MemoryMessageQueue",
    "RabbitMQMessageQueue",
    "get_message_queue",
]


class IMessageQueue(Protocol):
    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def publish(self, body: str) -> Any:
        """
        Get an item from the container
        """

    def subscribe(self) -> Iterable[Any]:
        """
        Set and item in the container
        """


class MemoryMessageQueue(IMessageQueue):
    def __init__(self, queue: str, topic: str):
        super().__init__()
        self._storage: SimpleQueue = SimpleQueue()
        self._queue = queue
        self._topic = topic

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def publish(self, body: str) -> None:
        print("MemoryMessageQueue: publish")
        self._storage.put_nowait(body)

    def subscribe(self) -> Iterable[Any]:
        while self._storage.qsize() > 0:
            item = self._storage.get_nowait()
            print("MemoryMessageQueue: subscribe")
            yield item


class RabbitMQMessageQueue(IMessageQueue):
    def __init__(self, uri: str, queue: str, topic: str):
        super().__init__()
        self._queue = queue
        self._topic = topic
        self._params = pika.URLParameters(uri)
        self._client: pika.BlockingConnection = None

    def __enter__(self) -> Any:
        self._client = pika.BlockingConnection(self._params)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        self._client.close()

    def publish(self, body: str) -> None:
        try:
            channel = self._client.channel()
            channel.queue_declare(queue=self._queue)
            channel.basic_publish(
                exchange="",
                routing_key=self._topic,
                body=body,
            )
            channel.close()
        except (pika.exceptions.ChannelError, pika.exceptions.StreamLostError):
            print(sys.exc_info())

    def subscribe(self) -> Iterable[Any]:
        channel = self._client.channel()
        data = channel.basic_get(self._topic, True)
        while data[0]:
            yield data[2]
            data = channel.basic_get(self._topic, True)
        channel.close()


def get_message_queue(
    queue: str, topic: str, settings: Settings = Settings()
) -> IMessageQueue:
    if settings.QUEUE_MODE == QueueMode.REMOTE:
        return RabbitMQMessageQueue(settings.MESSAGEQUEUE_URI, queue, topic)
    return MemoryMessageQueue(queue, topic)
