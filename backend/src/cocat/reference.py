"""
Reference
"""

from datetime import datetime
import os
from typing import Optional
from pydantic import BaseModel, validator, constr
from csv import DictReader

import pymongo
import logging
from .db import DB, PyObjectId
import motor.motor_asyncio

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
    updated: str = datetime.today().strftime("%Y-%m-%d")

    # class Settings:
    #     name = "references"
    #     indexes = [
    #         [
    #             ("name", pymongo.TEXT),
    #             ("name_en", pymongo.TEXT),
    #             ("name_fr", pymongo.TEXT),
    #             ("table_name", pymongo.TEXT),
        #     ],
        # ]
    @property
    def field(self):
        return self.table_name.replace("ref_", "")

    @property
    def name(self, lang: constr(regex="^(fr|en)$") = "fr"):
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
    def add(self) -> str:
        exists = self.get_by_name(self.name)
        if exists is not None:
            LOGGER.warning(f"<Reference(name='{self.name}'> already exists.")
            self.id = exists["_id"]

        else:
            self.id = DB.reference.insert_one(self.__dict__).inserted_id
            return self.id

    def delete(self) -> str:
        exists = self.get_by_name(self.name)
        if exists is None:
            LOGGER.warning(f"<Reference(name='{self.name}'> doesn't exist.")
        else:
            self.id = exists["_id"]
            DB.reference.delete_one({"_id": self.id})
            return self.id

    def get_by_id(self, id) -> dict:
        return DB.reference.find_one({"_id": id})

    def get_by_name(self, name) -> dict:
        return DB.reference.find_one({"$or": [{"name": name}, {"name_f": name}, {"name_en": name}]})


class Vocabulary:
    """
    Vocabulary
    
    Attributes
    ----------
    name: str
        name of the vocabulary
    lang: str
        language for vocabulary: fr or en default to fr
    
    references: list
        all the references given the name
    
    values: list
        all the name of the values in default lang

    uris: list
        all the uris of the vocabulary's values  
    
    Methods
    -------
    
    get_value: str
        retrieve the value of
    """

    def __init__(self, name: str, references: list, lang: constr(regex="^(fr|en)$") = "fr") -> None:
        self.name=name
        self.references=[r for r in references if r.table_name == self.name]
        self.lang = lang
    
    def get(self):
        if len(self.references) == 0:
            self.references = [Reference(**r) for r in DB.reference.find({"table_name": self.name})]
        return self.values


    @property
    def values(self) -> list:
        return [r.name for r in self.references]

    @property
    def uris(self) -> list:
        return [r.uri for r in self.references if r.uri is not None]
    

    def get_value(self, name) -> str:
        value= [r.get(f"name_{self.lang}") for r in self.references if r.get(
            f"name_{self.lang}") == name]
        if len(value) > 0:
           return value[0]
        else:
            return None
    
class CSVVocabularyBuilder:
    """
    CSVReferenceImporter

    Attributes
    ----------
    csv_file: str
        csv filepath
    """
    def __init__(self, csv_file):
        self.ref_file= csv_file    
        self.name  = self.ref_file.split("/")[-1].split(".")[0].replace("ref_", "")
        self.references = CSVReferenceImporter(csv_file)
    def build(self):
        return Vocabulary(self.name, self.ref_file)
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
        self.ref_file= csv_file    
        
    @property
    def references(self):
        references = []
        with open(self.ref_file, "r") as f:
            reader= DictReader(f, delimiter = ",")
            for row in reader:
                row["file"]= os.path.basename(self.ref_file)
                row["table_name"]= self.ref_file.split("/")[-1].split(".")[0].replace("ref_", "")
                r =  Reference.parse_obj(row)
                r.add()
                references.append(r)
        return references

    