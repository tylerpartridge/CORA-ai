
import redis
import os
import json
import logging
from pathlib import Path
from typing import Optional

# Configure logger
logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            config_file = Path("config/redis_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)['redis']
            else:
                config = {
                    'host': os.getenv('REDIS_HOST', 'localhost'),
                    'port': int(os.getenv('REDIS_PORT', 6379)),
                    'password': os.getenv('REDIS_PASSWORD'),
                    'db': int(os.getenv('REDIS_DB', 0))
                }
            
            self.redis_client = redis.Redis(
                host=config['host'],
                port=config['port'],
                password=config['password'],
                db=config['db'],
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Redis get error: {str(e)}")
        return None
    
    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in Redis with expiration"""
        if self.redis_client:
            try:
                return self.redis_client.setex(key, expire, value)
            except Exception as e:
                logger.error(f"Redis set error: {str(e)}")
        return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if self.redis_client:
            try:
                return bool(self.redis_client.delete(key))
            except Exception as e:
                logger.error(f"Redis delete error: {str(e)}")
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except Exception as e:
                logger.error(f"Redis exists error: {str(e)}")
        return False

# Global Redis instance
redis_manager = RedisManager()

def get_redis_client():
    """Get Redis client instance for direct access"""
    return redis_manager.redis_client
