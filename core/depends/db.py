from config import config
from pymongo import (
    AsyncMongoClient,
    MongoClient
)


sync_client = MongoClient(config.BF_MONGODB_URI, maxpoolsize = 100)
async_client = AsyncMongoClient(config.BF_MONGODB_URI, maxpoolsize = 100)


def get_sync_db():
    return sync_client[config.BF_MONGODB_DB]


def get_async_db():
    return async_client[config.BF_MONGODB_DB]
