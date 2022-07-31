"""
Reference
"""

from datetime import datetime

from typing import Optional, List
from pydantic import BaseModel, validator, constr, root_validator
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

    
    @root_validator
    def set_label(cls, values):
        if values["lang"] == "en":
            values["label"] = values["name_en"]
        
        else:
            values["label"] = values["name_fr"]
        return values


    @root_validator
    def set_name(cls, values):
        if values["lang"] == "en":
            values["name"] = values["name_en"]
        
        else:
            values["name"] = values["name_fr"]
        return values

    @root_validator
    def set_xml(cls, values):
        values["xml"] = f'''<{values["field"]}>
                <name>{values["name_en"]}</name>
                <description></description>
                <update date="{values["updated"]}"/>
            </{values["field"]}>
        '''
        return values

    @root_validator
    def exists(cls, values):
        values["exists"] = values["label"] is not None
        return values

    def add(self) -> bool:    
        exists = self.get_by_label(self.name)
        if exists is not None:
            LOGGER.warning(f"<Reference(name='{self.label}'> already exists.")
            self.id = exists["_id"]
            return False
        else:
            self.id = DB.reference.insert_one(self.__dict__).inserted_id
            return True
    
    def update(self, update_reference: dict) -> bool:
        if self.id is None:
            LOGGER.warning(
                f"<Reference(name='{self.label}'> doesn't exists.")
            return False
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
            return True
            
    def delete(self) -> bool:
        exists = self.get_by_label(self.name)
        if exists is None:
            LOGGER.warning(f"<Reference(name='{self.name}'> doesn't exist.")
            return False
        else:
            self.id = exists["_id"]
            DB.reference.delete_one({"_id": self.id})
            return True
        
    def get_by_id(self, id) -> dict:
        ref = DB.reference.find_one({"_id": id})
        if ref is None:
            return None
        return dict(ref)

    def get_by_label(self, name) -> dict:
        ref = DB.reference.find_one({"$or": [{"label": name}, {"name_fr": name}, {"name_en": name}]})
        if ref is None:
            return None
        return dict(ref)


    def get_by_lang(self, name, lang=constr(regex="^(fr|en)$")) -> dict:
        ref = DB.reference.find_one({f"name_{lang}": name})
        if ref is None:
            return None
        return dict(ref)
