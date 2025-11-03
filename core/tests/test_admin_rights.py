# import os

# import pytest
# from httpx import (
#     ASGITransport,
#     AsyncClient
# )
# from main import app
# from pymongo import AsyncMongoClient
# from pytest import fixture
# from tests.tutils import (
#     create_admin,
#     create_user
# )


# # Заменяем TestClient на асинхронную фикстуру с AsyncClient
# @pytest.fixture(scope="function")
# async def async_client():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         yield client


# @fixture(scope="function")
# async def mongodb():
#     mongo_client = AsyncMongoClient(os.environ["BF_MONGODB_URI"])
#     db = mongo_client[os.environ["BF_MONGODB_DB"]]
#     yield db
#     await db.drop_collection("users")
#     await mongo_client.close()


# @fixture
# async def admin(mongodb):
#     await mongodb.users.insert_one(create_admin())
#     yield
#     await mongodb.users.delete_one({"uuid.test": "admin"})


# @fixture
# async def regular(mongodb):
#     await mongodb.users.insert_one(create_user())
#     yield
#     await mongodb.users.delete_one({"uuid.test": "user"})


# async def test_add_user(admin, async_client: AsyncClient):
#     headers = {"app-auth-token": "test_secret"}
#     payload = {"initiator": ["test", "admin"], "target": ["test", "regular"], "username": "regular-user"}
#     response = await async_client.post("/api/admin/add-user", headers=headers, json=payload)
#     assert response.status_code == 200


# async def test_del_user(admin, regular, async_client: AsyncClient):
#     headers = {"app-auth-token": "test_secret"}
#     payload = {"initiator": ["test", "admin"], "target": ["test", "regular"]}
#     response = await async_client.post("/api/admin/del-user", headers=headers, json=payload)
#     assert response.status_code == 200

import os

from fastapi.testclient import TestClient
from main import app
from pymongo import MongoClient
from pytest import fixture
from tests.tutils import (
    create_admin,
    create_user
)


fclient = TestClient(app)


@fixture(scope="function")
def mongodb():
    mongoc = MongoClient(os.environ["BF_MONGODB_URI"])
    yield mongoc[os.environ["BF_MONGODB_DB"]]
    mongoc[os.environ["BF_MONGODB_DB"]].drop_collection("users")


@fixture
def admin(mongodb):
    mongodb.users.insert_one(create_admin())
    yield
    mongodb.users.delete_one({"uuid.internal": "admin"})


@fixture
def regular(mongodb):
    mongodb.users.insert_one(create_user())
    yield
    mongodb.users.delete_one({"uuid.internal": "regular"})


def test_add_rights(admin):
    headers = {"app-auth-token": "test_secret"}
    payload = {"initiator": ["internal", "admin"], "target": ["internal", "user"], "rights": ["all:full"]}
    response = fclient.post("/api/admin/add-rights", headers=headers, json = payload)
    assert response.status_code == 200


def test_del_rights(admin, regular):
    headers = {"app-auth-token": "test_secret"}
    payload = {"initiator": ["internal", "admin"], "target": ["internal", "user"], "rights": ["all:full"]}
    response = fclient.post("/api/admin/del-rights", headers=headers, json = payload)
    assert response.status_code == 200

# TODO Добавить тестов с неверным использованием эндпоинтов
