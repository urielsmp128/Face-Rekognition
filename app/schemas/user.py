def userEntity(item) -> dict | None:
    if item is None:
        return None
    password = ""
    if "password" in item:
        password = item["password"]
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "last_name": item["last_name"],
        "username": item["username"],
        "email": item["email"],
        "password": password,
        "status": item["status"],
        "created_at": item["created_at"],
        "updated_at": item["updated_at"],
    }


def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]
