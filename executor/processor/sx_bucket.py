from typing import Any
import globals as g


class Library:
    def __init__(self, db, plugin:str, sender: dict):
        self._sender = sender
        self._plugin = plugin
        self._db = db
    
    def get_bucket(self, codename: str):
        bucket = self._db.buckets.find_one({"plugin": self._plugin["codename"], "codename": codename}, {"items": {"$slice": -100}})
        #raise Exception(str({"plugin": self._plugin, "codename": codename}) + "    " + str(bucket))
        if not bucket:
            return None
        
        match bucket:
            case {"access": "common", "type": "list"}:
                return ListCommonBucket(self._db, bucket.get("plugin"), codename)
            case {"access": "common", "type": "dict"}:
                return DictCommonBucket(self._db, bucket.get("plugin"), codename)
            case {"access": "personal", "type": "list"}:
                return ListPersonalBucket(self._db, bucket.get("plugin"), codename)
            case {"access": "personal", "type": "dict"}:
                return DictPersonalBucket(self._db, bucket.get("plugin"), codename)
        
        return None


class BaseBucket:
    def __init__(self, db, plugin: str, codename: str):
        self._db = db
        self._plugin = plugin
        self._codename = codename
    
    def _get_bucket(self):
        return self._db.buckets.find_one({"plugin": self._plugin, "codename": self._codename}, {"items": {"$slice": -200}})

    def _push_item(self, item: Any):
        self._db.buckets.update_one({"plugin": self._plugin, "codename": self._codename}, {"$push": {self._path_to_items: item}})

    def _remove_item(self, item: Any):
        self._db.buckets.update_one({"plugin": self._plugin, "codename": self._codename}, {"$pull": {self._path_to_items: item}})
    
    def _pop_item(self, idx: int):
        return self._db.buckets.update_one({"plugin": self._plugin, "codename": self._codename}, {"$pop": {self._path_to_items: idx}})
    
    def _set_item(self, key: int, item: Any):
        self._db.buckets.update_one({"plugin": self._plugin, "codename": self._codename}, {"$set": {f"{self._path_to_items}.{key}": item}})

    def _delete_item(self, key: int):
        self._db.buckets.update_one({"plugin": self._plugin, "codename": self._codename}, {"$unset": {f"{self._path_to_items}.{key}": ""}})


class Common:
    _path_to_items = "items"
    def _get_items(self, doc: dict) -> Any:
        return doc["items"]
    

class Personal:
    user = -1
    def set_user(self, user: int):
        self.user = user

    @property
    def path_to_items(self) -> str:
        return f"{self._path_to_items}.{self.user}"
    
    def _get_items(self, doc: dict) -> Any:
        if not self.user:
            return None
        
        return doc["items"][self.user]


class List:
    def get(self, idx: int = -1) -> Any:
        return self._get_items(self._get_bucket())[idx]

    def push(self, item: Any):
        self._push_item(item)
    
    def remove(self, item: Any):
        self._remove_item(item)
    
    def pop(self, idx: int = -1) -> Any:
        return self._pop_item(idx)

    def slice(self, start: int = None, end: int = None):
        if start and not end:
            return self._get_items(self._get_bucket())[start:]
        elif not start and end:
            return self._get_items(self._get_bucket())[:end]
        elif start and end:
            return self._get_items(self._get_bucket())[start:end]
        else:
            return self._get_items(self._get_bucket())[:]

    @property
    def size(self) -> int:
        return len(self._get_items(self._get_bucket()))


class Dict:
    def get(self, key: str, default: Any = None) -> Any:
        return self._get_items(self._get_bucket())[key] or default
    
    def set(self, key: str, value: Any):
        self._set_item(key, value)
    
    def delete(self, key: str):
        self._delete_item(key)


class ListPersonalBucket(BaseBucket, List, Personal):
    def __init__(self, _db, plugin: str, codename: str):
        super().__init__(_db, plugin, codename)


class DictPersonalBucket(BaseBucket, Dict, Personal):
    def __init__(self, _db, plugin: str, codename: str):
        super().__init__(_db, plugin, codename)


class ListCommonBucket(BaseBucket, List, Common):
    def __init__(self, _db, plugin: str, codename: str):
        super().__init__(_db, plugin, codename)


class DictCommonBucket(BaseBucket, Dict, Common):
    def __init__(self, _db, plugin: str, codename: str):
        super().__init__(_db, plugin, codename)