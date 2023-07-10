from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import HTTPException, UploadFile, status

import app.services.user as UserService
import app.services.person as PersonService
import app.utils.rekognition as rekognition
from app.config.db import conn
from app.models.image import Image
from app.schemas.image import imageEntity, imagesEntity
from app.utils.config import settings
import uuid


COLLECTION = (conn[settings.DATABASE_NAME]).image


async def find_image(id: str) -> dict:
    return imageEntity(COLLECTION.find_one({"_id": ObjectId(id)}))


def search_faces_by_image(fileName: str) -> str:
    return rekognition.search_faces_by_image(fileName)


async def find_images(email: str, page: int = 0, size: int = 10) -> list:
    if page <= 0:
        return imagesEntity(COLLECTION.find({"user.email": email}).limit(size))
    skip = page * size
    return imagesEntity(
        COLLECTION.find({"user.email": email}).skip(skip).limit(size)
    )


def get_firs_payload(user):
    createdAt = datetime.now()
    return {
        "identification_id": "",
        "file_name": "",
        "person_count": 0,
        "persons": [],
        "status": 2,
        "error_msg": "",
        "created_at": createdAt,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "last_name": user["last_name"],
            "username": user["username"],
            "email": user["email"],
        },
    }


async def upload_image(email: str, files: List[UploadFile]) -> list:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No files found!"
        )

    extensionValid = True
    for file in files:
        ext = file.filename.split(".")[-1]

        if not (ext == "jpeg" or ext == "jpg" or ext == "png"):
            extensionValid = False

    if not extensionValid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or some of the files has an invalid extension",
        )

    results = []
    user = await UserService.find_user_by_email(email)

    for file in files:
        image = await upload_image_by_file(user, file)
        results.append(image)

    return results


async def upload_image_by_file(user, file: UploadFile) -> dict:
    image = await create_image(get_firs_payload(user))
    imageId = image["id"]

    fileContent = await file.read()
    ext = file.filename.split(".")[-1]
    fileName = f"{imageId}.{ext}"
    fileName2 = f"bounding/{imageId}.{ext}"

    await rekognition.s3_upload(contents=fileContent, key=fileName)
    new_image = await rekognition.show_faces(fileName)
    await rekognition.s3_upload(contents=new_image[0], key=fileName2)
    image["file_name"] = fileName
    image["status"] = 3
    image = await update_image_for_upload(imageId, image)

    persons = []
    detectFacesResponse = rekognition.detect_faces(fileName)
    if len(detectFacesResponse["FaceDetails"]) == 0:
        await rekognition.s3_delete(fileName)
        image["status"] = -1
        image["error_msg"] = "No faces found"
    elif len(detectFacesResponse["FaceDetails"]) == 1:
        personImage = await recognize_one_face(fileName, image, new_image)
        persons.append(personImage)
    else:
        persons = await recognize_multiple_faces(fileName, image, new_image)

    image["person_count"] = len(detectFacesResponse["FaceDetails"])

    tagged = 0
    unTagged = 0
    for person in persons:
        if person["name"] == "":
            unTagged += 1
        else:
            tagged += 1

    if unTagged == 0 or tagged == image["person_count"]:
        image["status"] = 1
    elif tagged != image["person_count"]:
        if tagged == 1:
            if image["person_count"] == 1:
                image["status"] = 3
            else:
                image["status"] = 4
        else:
            image["status"] = 3

    image["persons"] = persons
    image = await update_image_for_upload(imageId, image)
    return image


async def recognize_one_face(fileName: str, image, bounding_results) -> dict:
    list_colors = bounding_results[1]
    list_lefts = bounding_results[2]
    b_color = ""
    searchResponse = rekognition.search_faces_by_image(fileName)
    person = None
    personImage = None

    for faceInSearch in searchResponse["FaceMatches"]:
        identificationId = faceInSearch["Face"]["FaceId"]
        face = faceInSearch["Face"]
        person = await PersonService.find_person_by_identification_id(
            identificationId
        )
        b_color = list_colors[0]
        if person is not None:
            personImage = {
                "id": person["id"],
                "identification_id": person["identification_id"],
                "thumbnail_url": person["thumbnail_url"],
                "name": person["name"],
                "team": person["team"],
                "number": person["number"],
                "percentage": faceInSearch["Similarity"],
                "top": searchResponse["SearchedFaceBoundingBox"]["Top"],
                "left": searchResponse["SearchedFaceBoundingBox"]["Left"],
                "width": searchResponse["SearchedFaceBoundingBox"]["Width"],
                "height": searchResponse["SearchedFaceBoundingBox"]["Height"],
                "color": b_color,
            }
            break

    if person is None:
        indexResponse = rekognition.index_image(fileName)
        face = indexResponse["FaceRecords"][0]
        image["identification_id"] = face["Face"]["ImageId"]
        identificationId = face["Face"]["FaceId"]
        person = await PersonService.create_person(
            PersonService.get_first_payload(identificationId)
        )
        if face["Face"]["BoundingBox"]["Left"] in list_lefts:
            face_left = face["Face"]["BoundingBox"]["Left"]
            b_color_index = list_lefts.index(face_left)
            b_color = list_colors[b_color_index]
        personImage = {
            "id": person["id"],
            "identification_id": person["identification_id"],
            "thumbnail_url": person["thumbnail_url"],
            "name": person["name"],
            "team": "",
            "number": 0,
            "percentage": 100,
            "top": face["Face"]["BoundingBox"]["Top"],
            "left": face["Face"]["BoundingBox"]["Left"],
            "width": face["Face"]["BoundingBox"]["Width"],
            "height": face["Face"]["BoundingBox"]["Height"],
            "color": b_color,
        }
    return personImage


async def recognize_multiple_faces(
    fileName: str, image, bounding_results
) -> dict:
    list_colors = bounding_results[1]
    list_lefts = bounding_results[2]
    b_color = ""
    indexResponse = rekognition.index_image(fileName)
    personImage = None
    persons = []

    for indexFace in indexResponse["FaceRecords"]:
        identificationId = indexFace["Face"]["FaceId"]
        image["identificationId"] = indexFace["Face"]["ImageId"]
        face_left = "{:.4f}".format(indexFace["Face"]["BoundingBox"]["Left"])
        b_color_index = list_lefts.index(face_left)
        b_color = list_colors[b_color_index]
        personImage = {
            "id": "",
            "identification_id": "",
            "thumbnail_url": "",
            "name": "",
            "team": "",
            "number": 0,
            "percentage": 0,
            "top": indexFace["Face"]["BoundingBox"]["Top"],
            "left": indexFace["Face"]["BoundingBox"]["Left"],
            "width": indexFace["Face"]["BoundingBox"]["Width"],
            "height": indexFace["Face"]["BoundingBox"]["Height"],
            "color": b_color,
        }

        person = None
        searchResponse = rekognition.search_faces(identificationId)
        for searchFace in searchResponse["FaceMatches"]:
            searchId = searchFace["Face"]["FaceId"]

            person = await PersonService.find_person_by_identification_id(
                searchId
            )
            if person is not None:
                personImage["id"] = person["id"]
                personImage["identification_id"] = searchId
                personImage["thumbnail_url"] = person["thumbnail_url"]
                personImage["name"] = person["name"]
                personImage["team"] = person["team"]
                personImage["number"] = person["number"]
                personImage["percentage"] = searchFace["Similarity"]
                break

        if person is None:
            person = await PersonService.create_person(
                PersonService.get_first_payload(identificationId)
            )
            personImage["id"] = person["id"]
            personImage["identification_id"] = identificationId
            personImage["thumbnail_url"] = person["thumbnail_url"]
            personImage["percentage"] = 100

        persons.append(personImage)

    return persons


async def create_image(image: Image) -> dict:
    newImage = dict(image)
    id = COLLECTION.insert_one(newImage).inserted_id
    image = COLLECTION.find_one({"_id": id})
    return imageEntity(image)


async def search_by_image(email: str, file: UploadFile) -> list:
    fileName = await upload_image_for_search_by_file(file)
    similars = search_faces_by_image(fileName)["FaceMatches"]
    fileNameResp = fileName.replace(f"{settings.SEARCH_FILE_AWS_S3_DIR}/", "")

    ids = []
    for similar in similars:
        id = similar["Face"]["FaceId"]
        ids.append(id)

    images = COLLECTION.find(
        {
            "user.email": email,
            "status": {"$in": [1, 3, 4]},
            "persons.identification_id": {"$in": ids},
        }
    ).limit(settings.SEARCH_FILE_LIMIT)

    images = imagesEntity(images)
    return {"file_name": fileNameResp, "images": images}


async def upload_image_for_search_by_file(file: UploadFile) -> str:
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No files found!"
        )

    fileContent = await file.read()
    ext = file.filename.split(".")[-1]
    imageId = str(uuid.uuid1())
    fileName = f"{settings.SEARCH_FILE_AWS_S3_DIR}/{imageId}.{ext}"

    await rekognition.s3_upload(contents=fileContent, key=fileName)

    return fileName


async def delete_search_image(fileName: str) -> dict:
    await rekognition.s3_delete(
        f"{settings.SEARCH_FILE_AWS_S3_DIR}/{fileName}"
    )


async def delete_image(id: str) -> dict:
    COLLECTION.find_one_and_delete({"_id": ObjectId(id)})


async def find_images_by_name(
    email: str, q: str, page: int = 0, size: int = 10
) -> list:
    if page <= 0:
        return imagesEntity(
            COLLECTION.find(
                {
                    "user.email": email,
                    "status": {"$in": [1, 3, 4]},
                    "persons.name": {"$regex": q, "$options": "i"},
                }
            ).limit(size)
        )
    skip = page * size
    return imagesEntity(
        COLLECTION.find(
            {
                "user.email": email,
                "status": {"$in": [1, 3, 4]},
                "persons.name": {"$regex": q, "$options": "i"},
            }
        )
        .skip(skip)
        .limit(size)
    )


async def find_images_by_user(
    email: str, page: int = 0, size: int = 10
) -> list:
    if page <= 0:
        return imagesEntity(
            COLLECTION.find(
                {"user.email": email, "status": {"$in": [1, 3, 4]}}
            ).limit(size)
        )
    skip = page * size
    return imagesEntity(
        COLLECTION.find({"user.email": email, "status": {"$in": [1, 3, 4]}})
        .skip(skip)
        .limit(size)
    )


async def update_image_for_upload(id: str, image: Image) -> dict:
    if "id" in image:
        del image["id"]
    COLLECTION.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": dict(image)}
    )
    return imageEntity(COLLECTION.find_one({"_id": ObjectId(id)}))


async def update_image(id: str, image: Image) -> dict:
    imageDB = await find_image(id)

    if len(image.persons) > 0:
        for person in image.persons:
            for personDB in imageDB["persons"]:
                if (
                    person.name != personDB["name"]
                    or person.team != personDB["team"]
                    or person.number != personDB["number"]
                ):
                    await PersonService.update_name_person(
                        person.id, person.name, person.team, person.number
                    )
                    await update_name_person_from_image(
                        person.id, person.name, person.team, person.number
                    )

    return imageEntity(COLLECTION.find_one({"_id": ObjectId(id)}))


async def update_name_person_from_image(
    id: str, name: str, team: str, number: int
) -> list:
    COLLECTION.update_many(
        {"persons.id": id},
        {
            "$set": {
                "persons.$[elem].name": name,
                "persons.$[elem].team": team,
                "persons.$[elem].number": number,
            }
        },
        array_filters=[{"elem.id": id}],
        upsert=True,
    )

    images = imagesEntity(COLLECTION.find({"persons.id": id}))
    for image in images:
        complete = True
        for person in image["persons"]:
            if person["name"] == "":
                complete = False

        if complete:
            COLLECTION.find_one_and_update(
                {"_id": ObjectId(image["id"])}, {"$set": {"status": 1}}
            )

    return imagesEntity(COLLECTION.find({"persons.id": id}))
