from config import config
from pymongo import (
    AsyncMongoClient,
    MongoClient
)


# TODO Добавить обертку с IN-MEMORY кэшем для app_args
# TODO Добавить обертку с EXTERNAL кэшем для пользователей

if not config.BF_DEBUG:
    sync_client = MongoClient(config.BF_MONGODB_URI, maxpoolsize = 100)
    async_client = AsyncMongoClient(config.BF_MONGODB_URI, maxpoolsize = 100)

    def get_sync_db():  # type: ignore
        return sync_client[config.BF_MONGODB_DB]

    async def get_async_db():  # type: ignore
        return async_client[config.BF_MONGODB_DB]

elif config.BF_DEBUG:
    def get_sync_db():
        sync_client = MongoClient(config.BF_MONGODB_URI, maxpoolsize = 100)
        return sync_client[config.BF_MONGODB_DB]
        sync_client.close()

    async def get_async_db():
        async_client = AsyncMongoClient(config.BF_MONGODB_URI, maxpoolsize = 100)
        yield async_client[config.BF_MONGODB_DB]
        await async_client.close()
