import boto3
import io
import random
from PIL import Image, ImageDraw

from app.utils.config import settings

BUCKET_NAME = settings.AWS_BUCKET_NAME
client = boto3.client(
    "rekognition",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def search_faces_by_image(fileName: str) -> dict:
    image = {"S3Object": {"Bucket": BUCKET_NAME, "Name": fileName}}
    response = client.search_faces_by_image(
        CollectionId=settings.REKOGNITION_COLLECTION,
        Image=image,
        QualityFilter="HIGH",
        FaceMatchThreshold=95,
        MaxFaces=10,
    )

    faceMatches = response
    return faceMatches


def index_image(fileName: str) -> dict:
    response = client.index_faces(
        Image={"S3Object": {"Bucket": BUCKET_NAME, "Name": fileName}},
        CollectionId=settings.REKOGNITION_COLLECTION,
    )
    return response


def find_celebrity(fileName: str) -> dict:
    response = client.recognize_celebrities(
        Image={
            "S3Object": {
                "Bucket": BUCKET_NAME,
                "Name": fileName,
            }
        }
    )
    return response


def search_faces(id: str) -> dict:
    response = client.search_faces(
        CollectionId=settings.REKOGNITION_COLLECTION,
        FaceId=id,
        FaceMatchThreshold=95,
        MaxFaces=100,
    )
    return response


def detect_faces(fileName: str) -> dict:
    image = {"S3Object": {"Bucket": BUCKET_NAME, "Name": fileName}}
    response = client.detect_faces(Image=image)
    return response


def list_collections() -> dict:
    response = client.list_collections(MaxResults=10)
    return response


def create_collection(name: str) -> dict:
    response = client.create_collection(CollectionId=name)
    return response


def delete_collection(name: str) -> dict:
    response = client.delete_collection(CollectionId=name)
    return response


def list_faces() -> dict:
    response = client.list_faces(
        MaxResults=100, CollectionId=settings.REKOGNITION_COLLECTION
    )
    return response


async def s3_upload(contents: bytes, key: str):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(BUCKET_NAME)
    bucket.put_object(Key=key, Body=contents)


async def s3_delete(key: str):
    s3 = boto3.client("s3")
    s3.delete_object(Bucket=BUCKET_NAME, Key=key)


async def show_faces(photo):
    bounding_colors = []
    bounding_lefts = []
    random_number = random.randrange(0, 2**24)
    hex_number = str(hex(random_number))
    hex_number = "#" + hex_number[2:]

    # Load image from S3 bucket
    s3_connection = boto3.resource("s3")
    s3_object = s3_connection.Object(BUCKET_NAME, photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response["Body"].read())
    image = Image.open(stream)

    # Call DetectFaces
    response = client.detect_faces(
        Image={"S3Object": {"Bucket": BUCKET_NAME, "Name": photo}},
        Attributes=["ALL"],
    )

    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected face
    for faceDetail in response["FaceDetails"]:
        random_number = random.randint(0, 16777215)
        hex_number = str(hex(random_number))
        if len(hex_number) < 8:
            hex_number = hex_number + "0"
        hex_number = "#" + hex_number[2:]
        box = faceDetail["BoundingBox"]
        left = imgWidth * box["Left"]
        top = imgHeight * box["Top"]
        width = imgWidth * box["Width"]
        height = imgHeight * box["Height"]

        points = (
            (left, top),
            (left + width, top),
            (left + width, top + height),
            (left, top + height),
            (left, top),
        )
        draw.line(points, fill=hex_number, width=4)
        bounding_colors.append(hex_number)
        left_value = "{:.4f}".format(box["Left"])
        bounding_lefts.append(left_value)

        # Alternatively can draw rectangle. However you can't set line width.
        # draw.rectangle([left,top, left + width, top + height], outline='#00d400')
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format=image.format)
    in_mem_file.seek(0)
    saved_image = in_mem_file
    return [saved_image, bounding_colors, bounding_lefts]
