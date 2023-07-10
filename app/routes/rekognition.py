from fastapi import APIRouter

import app.utils.rekognition as Rekognition

TAG = "Rekognition"
PREFIX = "/rekognition"

rekognition = APIRouter()


@rekognition.get(
    PREFIX + "/list-collection",
    tags=[TAG],
)
async def list_collection():
    return Rekognition.list_collections()


@rekognition.get(
    PREFIX + "/list-face-collection",
    tags=[TAG],
)
async def list_face_collection():
    return Rekognition.list_faces()


@rekognition.get(
    PREFIX + "/create-collection",
    tags=[TAG],
)
async def create_collection(name: str):
    return Rekognition.create_collection(name)


@rekognition.delete(
    PREFIX + "/delete-collection",
    tags=[TAG],
)
async def delete_collection(name: str):
    return Rekognition.delete_collection(name)
