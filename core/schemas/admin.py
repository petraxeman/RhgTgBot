from pydantic import (
    BaseModel,
    Field
)


# Users Category

class AddUserRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)  # uuid_provider, UUID of initiator user
    target: list[str] = Field(min_length=2, max_length=2)  # uuid_provider, UUID of target user
    username: str = Field()  # username of target user


class DeleteUserRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)  # uuid_provider, UUID of initiator user
    target: list[str] = Field(min_length=2, max_length=2)  # uuid_provider, UUID of target user


class GetUsersListRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)  # uuid_provider, UUID of initiator user
    page: int = Field(gt=0)
    page_size: int = Field(gt=0, le=101)


class GetUserRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)  # uuid_provider, UUID of initiator user
    target: list[str] = Field(min_length=2, max_length=2)  # uuid_provider, UUID of target user


class UserUUIDResponse(BaseModel):
    uuid: str = Field()


class UsersListResponse(BaseModel):
    users: list[str] = Field(max_length=100)


class UserObjectResponse(BaseModel):
    user: dict = Field()


# Rights category

class AddRightsRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)
    target: list[str] = Field(min_length=2, max_length=2)
    rights: list[str] = Field(min_length=1)


class DelRightsRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)
    target: list[str] = Field(min_length=2, max_length=2)
    rights: list[str] = Field(min_length=1)


class GetRightsRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)
    target: list[str] = Field(min_length=2, max_length=2)


class GetSelfRightsRequest(BaseModel):
    initiator: list[str] = Field(min_length=2, max_length=2)


class GetRightsResponse(BaseModel):
    user: list[str] = Field(min_length=2, max_length=2)
    rights: list[str] = Field()


# App settings category

class GetAppArgsResponse(BaseModel):
    args_map: dict[str, str] = Field()


class SetAppArgsRequest(BaseModel):
    args_map: dict[str, str] = Field()
