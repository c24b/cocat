"""
Reference
"""

from datetime import datetime

from typing import Optional, List
from pydantic import BaseModel, validator, constr

import pymongo
import logging
from cocat.db import DB, PyObjectId
import motor.motor_asyncio

LOGGER = logging.getLogger(__name__)
# from bson.objectid import ObjectId as BsonObjectId


class Reference(BaseModel):
    """
    Reference

    Attributes
    ----------
    vocabulary: str
        name of the table for the reference set
    field: str
        field of the reference
    file: str
        csv filename of the initial reference table
    name_en: Optional[str]
        value of the reference in english
    name_fr: str
        value of the reference in french
    uri: Optional[str]
        standard uri for the reference
    slug: Optional[str]
        shortcode for the reference

    Methods
    -------
    set_name()
    """

    id: Optional[PyObjectId] = None
    vocabulary: str = None
    field: str = None
    name_en: Optional[str] = None
    name_fr: str = None
    label: Optional[str] = None
    uri: Optional[str] = None
    slug: Optional[str] = None
    lang: constr(regex="^(fr|en)$") = "fr"
    updated: str = datetime.today().strftime("%Y-%m-%d")
    standards: Optional[List] = []

    @property
    def field(self):
        return self.vocabulary.replace("ref_", "")

    @property
    def label(self):
        if self.lang == "en":
            return self.name_en
        return self.name_fr

    @property
    def name(self):
        if self.lang == "en":
            return self.name_en
        return self.name_fr

    @property
    def xml(self):
        return f'''<{self.field}>
                <name>{self.name_en}</name>
                <description></description>
                <update date="{self.updated}"/>
            </{self.field}>
        '''

    def add(self) -> (bool, str):
        exists = self.get_by_label(self.label)
        if exists is not None:
            LOGGER.warning(f"<Reference(name='{self.label}'> already exists.")
            self.id = exists["_id"]
            return False, self.id
        else:
            self.id = DB.reference.insert_one(self.__dict__).inserted_id
            return True, self.id

    def update(self, update_reference: dict) -> (bool, str):
        if self.id is None:
            LOGGER.warning(
                f"<Reference(name='{self.label}'> doesn't exists.")
            return False, None
        else:
            invalid_keys = []
            exists = self.get_by_id(self.id)
            for k, v in update_reference.items():
                try:
                    setattr(self, k, v)
                except ValueError:
                    invalid_keys.append(k)
                    pass
            DB.reference.update_one({"_id": exists["_id"]}, {"$set": {k: v for k, v in update_reference.items() if k not in invalid_keys}})
            return True, self.id
            
    def delete(self) -> (bool, str):
        exists = self.get_by_label(self.name)
        if exists is None:
            LOGGER.warning(f"<Reference(name='{self.name}'> doesn't exist.")
            return False, None
        else:
            self.id = exists["_id"]
            DB.reference.delete_one({"_id": self.id})
            return True, self.id

    def get_by_id(self, id) -> dict:
        return DB.reference.find_one({"_id": id})

    def get_by_label(self, name) -> dict:
        return DB.reference.find_one({"$or": [{"label": name}, {"name_f": name}, {"name_en": name}]})

    def get_by_lang_name(self, name, lang=constr(regex="^(fr|en)$")) -> dict:
        return DB.reference.find_one({f"name_{lang}": name})
