
import os
import json
import logging
from pathlib import Path
from typing import Optional, Any, Iterable

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional in dev
    redis = None  # allow dev mode without redis installed

# Configure logger
logger = logging.getLogger(__name__)


class NullRedis:
    """No-op Redis shim for local/dev without a server."""

    def get(self, key: str) -> Optional[str]:
        return None

    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        return True

    def delete(self, key: str) -> bool:
        return False

    def exists(self, key: str) -> bool:
        return False

    def ping(self) -> bool:
        return False

    def close(self) -> None:  # synchronous no-op close
        return None

    def publish(self, channel: str, message: str) -> int:
        return 0

    def subscribe(self, channel: str) -> Iterable[Any]:
        return []


class RedisManager:
    def __init__(self):
        self.redis_client: Any = None
        self.client: Any = None  # compatibility alias used elsewhere
        self._connect()

    def _redact_url(self, url: str) -> str:
        try:
            # redact credentials if present
            if "@" in url and "://" in url:
                scheme, rest = url.split("://", 1)
                if "@" in rest:
                    auth, host = rest.split("@", 1)
                    return f"{scheme}://***:***@{host}"
        except Exception:
            pass
        return url

    def _connect(self) -> None:
        """Connect to Redis if configured; otherwise use NullRedis."""
        url = os.getenv("REDIS_URL") or os.getenv("CORA_REDIS_URL")
        if not url or redis is None:
            # No configuration: use no-op client
            self.redis_client = NullRedis()
            self.client = self.redis_client
            logger.info("Redis disabled (no REDIS_URL)")
            return

        try:
            # Prefer URL-based configuration when provided
            self.redis_client = redis.from_url(  # type: ignore[attr-defined]
                url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection quietly
            try:
                self.redis_client.ping()
                logger.info(f"Redis enabled: {self._redact_url(url)}")
            except Exception:
                # If ping fails, fall back to NullRedis for dev stability
                self.redis_client = NullRedis()
                logger.info("Redis disabled (unavailable)")
            self.client = self.redis_client
        except Exception:
            self.redis_client = NullRedis()
            self.client = self.redis_client
            logger.info("Redis disabled (unavailable)")

    # Public API passthroughs (preserve existing interface)
    def get(self, key: str) -> Optional[str]:
        try:
            return self.redis_client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        try:
            # Use setex when available
            if hasattr(self.redis_client, "setex"):
                return bool(self.redis_client.setex(key, expire, value))
            return bool(self.redis_client.set(key, value))
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        try:
            return bool(self.redis_client.exists(key))
        except Exception:
            return False

    def ping(self) -> bool:
        try:
            return bool(self.redis_client.ping())
        except Exception:
            return False

    async def close(self) -> None:
        try:
            close_fn = getattr(self.redis_client, "close", None)
            if callable(close_fn):
                res = close_fn()
                # Await if the client returns an awaitable
                try:
                    await res  # type: ignore[misc]
                except TypeError:
                    pass
        except Exception:
            # swallow to keep shutdown quiet
            pass

    # Additional passthroughs used elsewhere occasionally
    def publish(self, channel: str, message: str) -> int:
        try:
            return int(self.redis_client.publish(channel, message))
        except Exception:
            return 0

    def subscribe(self, channel: str) -> Iterable[Any]:
        try:
            return self.redis_client.subscribe(channel)
        except Exception:
            return []


# Global Redis instance
redis_manager = RedisManager()


def get_redis_client():
    """Get Redis client instance for direct access."""
    return redis_manager.redis_client
