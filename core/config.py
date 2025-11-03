from pydantic_settings import BaseSettings


class Configuration(BaseSettings):
    BF_ACCESS_KEY: str = ""
    BF_ADMIN_USERNAME: str = ""
    BF_MONGODB_URI: str = "mongodb://user:password@localhost:27017"
    BF_MONGODB_DB: str = "bobbyforge"
    BF_DEBUG: bool = False
    BF_DEFAULT_RIGHTS: str = ""

    def model_post_init(self, __context):
        self.BF_DEFAULT_RIGHTS = [r.strip() for r in self.BF_DEFAULT_RIGHTS.split(",") if r != ""]  # type: ignore


config = Configuration()
