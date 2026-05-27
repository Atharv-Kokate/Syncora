import asyncio
import structlog
from app.core.redis_client import get_redis

logger = structlog.get_logger()

class RedisPubSubManager:
    """
    Manages Redis Pub/Sub subscriptions for the collaboration nodes.
    Routes incoming binary Yjs updates from Redis channels to local WebSocket clients.
    """
    def __init__(self):
        self.pubsub = None
        self._listener_task = None
        # Maps channel name (e.g. "doc:<id>") to a list of async callback functions
        self._callbacks: dict[str, list] = {}

    async def connect(self):
        """Initializes the pubsub object and starts the background listener."""
        redis = get_redis()
        self.pubsub = redis.pubsub()
        self._listener_task = asyncio.create_task(self._listen())
        logger.info("redis_pubsub_manager_started")

    async def disconnect(self):
        """Cleans up the listener task and closes pubsub."""
        if self._listener_task:
            self._listener_task.cancel()
        if self.pubsub:
            await self.pubsub.close()
        logger.info("redis_pubsub_manager_stopped")

    async def subscribe(self, channel: str, callback):
        """Subscribes a callback to a specific document channel."""
        if channel not in self._callbacks:
            self._callbacks[channel] = []
            await self.pubsub.subscribe(channel)
            logger.info("redis_channel_subscribed", channel=channel)
            
        self._callbacks[channel].append(callback)

    async def unsubscribe(self, channel: str, callback):
        """Unsubscribes a callback from a document channel."""
        if channel in self._callbacks:
            try:
                self._callbacks[channel].remove(callback)
            except ValueError:
                pass
                
            if not self._callbacks[channel]:
                # No more local clients listening to this document
                del self._callbacks[channel]
                await self.pubsub.unsubscribe(channel)
                logger.info("redis_channel_unsubscribed", channel=channel)

    async def publish(self, channel: str, message: bytes):
        """Publishes a binary message to a specific document channel."""
        redis = get_redis()
        await redis.publish(channel, message)

    async def _listen(self):
        """Background task that actively waits for incoming Redis messages."""
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    # Extract channel and binary data
                    channel = message["channel"]
                    if isinstance(channel, bytes):
                        channel = channel.decode('utf-8')
                        
                    data = message["data"] # This must remain raw bytes
                    
                    callbacks = self._callbacks.get(channel, [])
                    for cb in callbacks:
                        try:
                            # Forward the binary payload to the local WebSocket associated with this callback
                            await cb(data)
                        except Exception as e:
                            logger.error("redis_callback_execution_failed", error=str(e), channel=channel)
                            
        except asyncio.CancelledError:
            logger.info("redis_listener_cancelled")
        except Exception as e:
            logger.error("redis_listener_crash", error=str(e))

# Global singleton instance
pubsub_manager = RedisPubSubManager()
