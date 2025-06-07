import globals as g


class BucketsLib:
    def __init__(self, sender: dict):
        self.__sender = sender
    
    async def get_bucket(self, codename: str, at_user: int = None):
        if bucket := await g.buckets.find_one({"codename": codename}):
            return bucket
        return {}


class BucketFactory:
    def __init__(self):
        pass
    
    def build(self, bukcet: dict):
        pass



    