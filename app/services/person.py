from datetime import datetime

from bson import ObjectId

from app.config.db import conn
from app.models.person import Person
from app.schemas.person import personEntity, personsEntity
from app.utils.config import settings

COLLECTION = (conn[settings.DATABASE_NAME]).person


async def find_person_by_id(id: str) -> dict:
    return personEntity(COLLECTION.find_one({"_id": ObjectId(id)}))


async def find_persons_by_name(name: str) -> dict:
    return personEntity(COLLECTION.find({"name": name}))


async def find_persons(page: int = 0, size: int = 10) -> list:
    if page <= 0:
        return personsEntity(COLLECTION.find().limit(size))
    skip = page * size
    return personsEntity(COLLECTION.find().skip(skip).limit(size))


async def create_person(person: Person) -> dict:
    newPerson = dict(person)
    if "id" in newPerson:
        del newPerson["id"]
    id = COLLECTION.insert_one(newPerson).inserted_id
    person = COLLECTION.find_one({"_id": id})
    return personEntity(person)


async def update_person(id: str, person: Person) -> dict:
    COLLECTION.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": dict(person)}
    )
    return personEntity(COLLECTION.find({"_id": ObjectId(id)}))


async def delete_person(id: str):
    COLLECTION.find_one_and_delete({"_id": ObjectId(id)})


async def find_person_by_identification_id(identificationId: str) -> dict:
    person = COLLECTION.find_one({"identification_id": identificationId})
    if person is None:
        return None
    return personEntity(person)


def get_first_payload(identificationId):
    datetimeNow = datetime.now()
    return {
        "identification_id": identificationId,
        "name": "",
        "team": "",
        "number": 0,
        "thumbnail_url": "",
        "status": 1,
        "created_at": datetimeNow,
        "updated_at": datetimeNow,
    }


async def update_name_person(
    id: str, name: str, team: str, number: int
) -> dict:
    COLLECTION.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {"name": name, "team": team, "number": number}},
    )
    return personEntity(COLLECTION.find_one({"_id": ObjectId(id)}))
