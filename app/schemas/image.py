def imageEntity(item) -> dict:
    if item is None:
        return None
    fileName = ""
    if "file_name" in item:
        fileName = item["file_name"]
    return {
        "id": str(item["_id"]),
        "identification_id": item["identification_id"],
        "file_name": fileName,
        "person_count": item["person_count"],
        "persons": item["persons"],
        "status": item["status"],
        "error_msg": item["error_msg"],
        "created_at": item["created_at"],
        "user": item["user"],
    }


def imagesEntity(entity) -> list:
    return [imageEntity(item) for item in entity]
