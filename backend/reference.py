"""
Reference
"""
import os
from typing import Optional
from pydantic import BaseModel, validator, constr
from csv import DictReader

# from beanie import Document, Indexed, init_beanie
import logging
from .db import DB, PyObjectId

LOGGER = logging.getLogger(__name__)
# from bson.objectid import ObjectId as BsonObjectId


class Reference(BaseModel):
    """
    Reference

    Attributes
    ----------
    table_name: str
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
    table_name: str = None
    field: str = None
    file: Optional[str] = None
    name_en: Optional[str] = None
    name_fr: str = None
    name: Optional[str] = None
    uri: Optional[str] = None
    slug: Optional[str] = None
    lang: str = "fr"

    @property
    def field(self):
        return self.table_name.replace("ref_", "")

    @property
    def name(self, lang: constr(regex="^(fr|en)$") = "fr"):
        if self.lang == "en":
            return self.name_en
        return self.name_fr

    def add(self):
        exists = self.get_by_name(self.name) 
        if exists is not None:
            LOGGER.warning(f"<Reference(name='{self.name}'> already exists.")
            self.id = exists["_id"]
            
        else:    
            self.id = DB.reference.insert_one(self.__dict__).inserted_id
            return self.id
    
    def delete(self):
        exists = self.get_by_name(self.name) 
        if exists is None:
            LOGGER.warning(f"<Reference(name='{self.name}'> doesn't exist.")
        else:
            self.id = exists["_id"]
            DB.reference.delete_one({"_id": self.id})
            return self.id
    
    def get_by_id(self, id):
        return DB.reference.find_one({"_id": id})
    
    def get_by_name(self, name):
        return DB.reference.find_one({"$or":[{"name": name}, {"name_f": name}, {"name_en": name}]})

class CSVReferenceImporter:
    """
    CSVReferenceImporter

    Attributes
    ----------
    csv_file: str
        csv filepath
    references: list
        list of Reference


    Methods
    -------
    set_references()
    """

    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.references = []
        self.set_reference()

    def set_references(self):
        with open(self.csv_file, "r") as f:
            reader = DictReader(f, delimiter=",")
            for row in reader:
                row["file"] = os.path.basename(self.csv_file)
                row["table_name"] = os.path.splitext(row["ref_file"])[0]
                r = Reference.parse_obj(row)
                self.references.append(r)

    def insert_references(self):
        for ref in self.references:
            DB.references.insert(ref)
