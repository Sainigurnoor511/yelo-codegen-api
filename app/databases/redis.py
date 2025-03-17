import redis.asyncio as redis
from ..utils.logger import setup_logger

logger = setup_logger()
redis_client = None

async def get_redis():
    global redis_client

    if redis_client is None:
        redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        logger.info("Connection to Redis successful.")

        # Automatically clear expired keys via TTL
        keys = await redis_client.keys("rate_limit:*")
        for key in keys:
            ttl = await redis_client.ttl(key)
            if ttl == -1:  # If no TTL is set
                await redis_client.expire(key, 604800)  # Set TTL to 1 week

        # TODO: Remove this block after testing
        #     # Clear rate limit keys on startup
        #     keys = await redis_client.keys("rate_limit:*")
        #     if keys:
        #         await redis_client.delete(*keys)
        #         print("✅ Redis rate limits cleared on app restart.")
        
        logger.info("Rate limit keys refreshed.")

    return redis_client
