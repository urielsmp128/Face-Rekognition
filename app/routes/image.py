from typing import List

from fastapi import APIRouter, Depends, Request, UploadFile

import app.services.image as Service
from app.models.image import Image
from app.utils.auth import AuthHandler
from app.utils.errors_handler import responses
from app.utils.JWTBearer import JWTBearer

TAG = "Image"
PREFIX = "/images"

image = APIRouter()
authhandler = AuthHandler()


@image.get(PREFIX + "/{id}", dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_image_by_id(id: str):
    resp = await Service.find_image(id)
    if resp is None:
        return responses[404]
    return resp


@image.get(
    PREFIX + "/{fileName}/similar",
    dependencies=[Depends(JWTBearer())],
    tags=[TAG],
)
async def find_similar_image(fileName: str):
    resp = await Service.search_faces_by_image(fileName)
    if resp is None:
        return responses[404]
    return resp


@image.get("/search" + PREFIX, dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_images_by_name(
    request: Request, q: str, page: int = 0, size: int = 10
):
    authorization = (request.headers.get("Authorization")).replace(
        "Bearer ", ""
    )
    email = authhandler.decode_token(authorization)
    return await Service.find_images_by_name(email, q, page, size)


@image.get(PREFIX, dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_images(request: Request, page: int = 0, size: int = 10):
    authorization = (request.headers.get("Authorization")).replace(
        "Bearer ", ""
    )
    email = authhandler.decode_token(authorization)
    return await Service.find_images(email, page, size)


@image.post(
    PREFIX + "/upload", dependencies=[Depends(JWTBearer())], tags=[TAG]
)
async def upload_image(request: Request, files: List[UploadFile]):
    authorization = (request.headers.get("Authorization")).replace(
        "Bearer ", ""
    )
    email = authhandler.decode_token(authorization)
    resp = await Service.upload_image(email, files)
    if resp is None:
        return responses[500]
    return resp


@image.post(
    "/search" + PREFIX + "/file",
    dependencies=[Depends(JWTBearer())],
    tags=[TAG],
)
async def search_by_image(request: Request, file: UploadFile):
    authorization = (request.headers.get("Authorization")).replace(
        "Bearer ", ""
    )
    email = authhandler.decode_token(authorization)
    return await Service.search_by_image(email, file)


@image.put(PREFIX + "/{id}", dependencies=[Depends(JWTBearer())], tags=[TAG])
async def update_image(id: str, image: Image):
    resp = await Service.update_image(id, image)
    if resp is None:
        return responses[404]
    return resp


@image.delete(
    PREFIX + "/{id}", dependencies=[Depends(JWTBearer())], tags=[TAG]
)
async def delete_image(id: str):
    await Service.delete_image(id)
    return responses[204]


@image.delete(
    PREFIX + "/search/{fileName}",
    dependencies=[Depends(JWTBearer())],
    tags=[TAG],
)
async def delete_search_image(fileName: str):
    await Service.delete_search_image(fileName)
    return responses[204]


@image.get(
    PREFIX + "/user/upload", dependencies=[Depends(JWTBearer())], tags=[TAG]
)
async def find_images_by_user(request: Request, page: int = 0, size: int = 10):
    authorization = (request.headers.get("Authorization")).replace(
        "Bearer ", ""
    )
    email = authhandler.decode_token(authorization)
    return await Service.find_images_by_user(email, page, size)
