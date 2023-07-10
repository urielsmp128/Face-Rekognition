from pymongo import MongoClient
from app.utils.config import settings

conn = MongoClient(settings.DATABASE_CONNECTION_URL)
