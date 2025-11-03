from depends.db import get_async_db
from depends.rights import verify_user
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)
from pymongo.asynchronous.database import AsyncDatabase
from schemas.admin import (
    GetAppArgsResponse,
    SetAppArgsRequest
)


router = APIRouter()


@router.post("/add-user", response_model=GetAppArgsResponse, status_code=status.HTTP_200_OK)
async def add_user(request: Request, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("add_user"))):
    args = await db.meta.find_one({"type": "global_variables"})
    if not args:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Somthing very worst in gettings args happends.")
    return {"args_map": args["value"]}


@router.post("/del-user", status_code=status.HTTP_200_OK)
async def del_user(request: SetAppArgsRequest, db: AsyncDatabase = Depends(get_async_db), initiator: dict = Depends(verify_user("del_user"))):
    await db.meta.update_one({"type": "global_variables"}, request.args_map)
    return {}
