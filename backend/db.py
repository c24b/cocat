import os
from pymongo import MongoClient
from  pymongo import errors as PyMongoError
from bson import ObjectId

# from settings import settings

import os
from dotenv import load_dotenv

load_dotenv()

mongodb_client = MongoClient(os.getenv("DB_URI"))
DB = mongodb_client[os.getenv("DB_NAME")]



class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")