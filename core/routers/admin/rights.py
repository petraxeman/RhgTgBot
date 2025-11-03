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
    AddRightsRequest,
    DelRightsRequest,
    GetRightsRequest,
    GetRightsResponse,
    GetSelfRightsRequest
)


router = APIRouter()


@router.post("/add-rights", status_code=status.HTTP_200_OK)
async def add_rights(request: AddRightsRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("add_rights"))):
    try:
        await db.users.update_one({"uuid": {request.target[0]: request.target[1]}}, {"$push": {"rights": {"$each": request.rights}}})
        return {}
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Somthing went wrong.")


# TODO Убрать возможность у имеющих права all:full удалять у себя права all:full
# TODO Метод будет успешен даже если у пользователя таких прав не было, это неправильно. Добавить ошибку
@router.post("/del-rights", status_code=status.HTTP_200_OK)
async def del_rights(request: DelRightsRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("del_rights"))):
    try:
        await db.users.update_one({"uuid": {request.target[0]: request.target[1]}}, {"$pull": {"rights": {"$in": request.rights}}})
        return {}
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Somthing went wrong.")


@router.post("/get-rights", response_model=GetRightsResponse, status_code=status.HTTP_200_OK)
async def get_rights(request: GetRightsRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("get_rights"))):
    user = await db.users.find_one({"uuid": {request.target[0]: request.target[1]}})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"rights": user["rights"], "user": ["internal", user["uuid"]["internal"]]}


@router.post("/get-self-rights", response_model=GetRightsResponse, status_code=status.HTTP_200_OK)
async def get_self_rights(request: GetSelfRightsRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("get_self_rights"))):
    return {"rights": initiator["rights"], "user": ["internal", initiator["uuid"]["internal"]]}
