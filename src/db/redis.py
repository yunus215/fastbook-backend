import redis.asyncio as aioredis
from src.config import Config


JTI_EXPIRY = 3600

# token_blacklist = aioredis.Redis(
#     host=Config.REDIS_HOST,
#     port=Config.REDIS_PORT,
#     db=0,
#     decode_responses=True,
# )

token_blacklist = aioredis.from_url(Config.REDIS_URL)


async def add_jti_to_blacklist(jti: str):
    await token_blacklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def token_in_blacklist(jti: str) -> bool:
    value = await token_blacklist.get(jti)
    # print("JTI KEY:", jti)
    return value is not None
