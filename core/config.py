from pydantic_settings import BaseSettings


class Configuration(BaseSettings):
    BF_ACCESS_KEY: str = ""
    BF_ADMIN_USERNAME: str = ""
    BF_MONGODB_URI: str = "mongodb://user:password@localhost:27017"
    BF_MONGODB_DB: str = "bobbyforge"
    BF_DEBUG: bool = False
    BF_DEFAULT_RIGHTS: list[str] = []


config = Configuration()
