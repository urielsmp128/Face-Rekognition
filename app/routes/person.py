from fastapi import APIRouter, status, Depends

import app.services.person as Service

from app.models.person import Person
from app.utils.errors_handler import responses
from app.utils.JWTBearer import JWTBearer

TAG = "Person"
PREFIX = "/persons"

person = APIRouter()


@person.get(PREFIX + "/{id}", dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_person_by_id(id: str):
    resp = await Service.find_person_by_id(id)
    if resp is None:
        return responses[404]
    return resp


@person.get(
    PREFIX + "/name/{name}", dependencies=[Depends(JWTBearer())], tags=[TAG]
)
async def find_persons_by_name(name: str):
    resp = await Service.find_persons_by_name(name)
    if resp is None:
        return responses[404]
    return resp


@person.get(PREFIX, dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_persons(page: int = 0, size: int = 10):
    return await Service.find_persons(page, size)


@person.post(PREFIX, dependencies=[Depends(JWTBearer())], tags=[TAG])
async def create_person(person: Person):
    resp = await Service.create_person(person)
    if resp is None:
        return responses[404]
    return resp


@person.put(PREFIX + "/{id}", dependencies=[Depends(JWTBearer())], tags=[TAG])
async def update_person(id: str, person: Person):
    resp = await Service.update_person(id, person)
    if resp is None:
        return responses[404]
    return resp


@person.delete(
    PREFIX + "/{id}",
    dependencies=[Depends(JWTBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[TAG],
)
async def delete_person(id: str):
    await Service.delete_person(id)
    return responses[204]
