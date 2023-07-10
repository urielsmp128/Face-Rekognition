def personEntity(item) -> dict:
    if item is None:
        return None
    return {
        "id": str(item["_id"]),
        "identification_id": item["identification_id"],
        "name": item["name"],
        "team": item["team"],
        "number": item["number"],
        "thumbnail_url": item["thumbnail_url"],
        "status": item["status"],
        "created_at": item["created_at"],
        "updated_at": item["updated_at"],
    }


def personsEntity(entity) -> list:
    return [personEntity(item) for item in entity]
