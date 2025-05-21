import globals as g



def create_bucket(project: str, config: dict):
    bucket = config.copy()
    
    del bucket["name"]
    if bucket["type"] == "list":
        bucket["storage"] = []
    elif bucket["type"] == "dict":
        bucket["storage"] = {}
    
    with g.db.transaction() as conn:
        conn.root.buckets[f"{project}.{config['name']}"] = bucket


def delete_bucket(project: str, name: str):
    with g.db.transaction() as conn:
        conn.root.buckets[f"{project}.{name}"] = None