from depends.db import get_async_db
from depends.rights import verify_user
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from pymongo.asynchronous.database import AsyncDatabase
from schemas.admin import (
    AddUserRequest,
    DeleteUserRequest,
    GetUserRequest,
    GetUsersListRequest,
    UserObjectResponse,
    UsersListResponse,
    UserUUIDResponse
)
from utils.db import create_user


router = APIRouter()


@router.post("/add-user", response_model=UserUUIDResponse, status_code=status.HTTP_200_OK)
async def add_user(request: AddUserRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("add_user"))):
    user: dict = await db.users.find_one({"username": request.username}) or {}
    if user:
        raise HTTPException(status.HTTP_409_CONFLICT, "This user already exists.")
    user = create_user(request.username, request.target[0], request.target[1])
    await db.users.insert_one(user)
    return {"uuid": user["uuid"]["internal"]}


@router.post("/del-user", status_code=status.HTTP_200_OK)
async def del_user(request: DeleteUserRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("del_user"))):
    user: dict | None = await db.users.find_one({f"uuid.{request.target[0]}": request.target[1]})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This user don't exists.")
    await db.users.delete_one({f"uuid.{request.target[0]}": request.target[1]})
    return {}


@router.post("/get-user", response_model=UserObjectResponse, status_code=status.HTTP_200_OK)
async def get_user(request: GetUserRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("get_user"))):
    user: dict | None = await db.users.find_one({f"uuid.{request.target[0]}": request.target[1]})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    del user["_id"]
    return user


@router.post("/get-users-list", response_model=UsersListResponse, status_code=status.HTTP_200_OK)
async def get_users_list(request: GetUsersListRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("get_users_list"))):
    users: list[dict] = list(await db.users.find({}).sort([("_id", 1)]).skip((request.page - 1) * request.page_size).limit(request.page_size).to_list())
    return {"users": [user["uuid"]["internal"] for user in users]}
