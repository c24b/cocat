
import os
from csv import DictReader
from typing import Optional, List
from pydantic import BaseModel, validator, constr
import pymongo
import logging
from cocat.db import DB, PyObjectId
from cocat.reference import Reference

class Vocabulary(BaseModel):
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
    build_references
    get_value: str
        retrieve the value of
    """
    id: Optional[PyObjectId] = None
    name: str = None
    lang: constr(regex="^(fr|en)$") = "fr"
    csv_file: Optional[str] = None
    filename: Optional[str]
    references: Optional[List[Reference]] = []
    db_name: Optional[str] = "reference"
    standards: Optional[List] = []

    # @validator("lang", pre=True)
    # def check_lang(cls, value, pre=True) -> str:
    #     if value not in ["en", "fr"]:
    #         raise ValueError(
    #             "Lang {value} is not supported: choose languages between 'en' or 'fr'")
    #     else:
    #         return value

    @property
    def labels(self) -> list:
        return [r.label for r in self.references]

    @property
    def names_en(self) -> list:
        return [r.name_en for r in self.references]

    @property
    def names_fr(self) -> list:
        return [r.name_fr for r in self.references]

    @property
    def uris(self) -> list:
        return [r.uri for r in self.references if r.uri is not None]

    def create(self, csv_file) -> list:
        self.filename = os.path.basename(csv_file)
        self.references = []
        with open(csv_file, "r") as f:
            reader = DictReader(f, delimiter=",")
            for row in reader:
                row["file"] = os.path.basename(self.filename)
                row["vocabulary"] = self.name
                row["lang"] = self.lang
                r = Reference.parse_obj(row)
                r.add()
                self.references.append(r)
        return self.references

    def delete(self) -> None:
        for ref in self.references:
            ref.delete()
        pass

    def add_reference(self, reference: Reference):
        reference["lang"] = self.lang
        r = Reference(**reference)
        r.add()
        self.references.append(r)
        return self.references

    def delete_reference(self, reference: Reference):
        r = Reference(**reference)
        r.delete()
        self.references.remove(r)
        return self.references

    def update_reference(self, reference_label, reference: Reference):
        existing_r = Reference(
            label=reference_label)
        self.references.delete(existing_r)
        updated_r = existing_r.update(reference)
        self.references.append(updated_r)
        return self.references

    def get_references(self):
        if len(self.references) == 0:
            self.references = [
                Reference(**r) for r in DB.reference.find({"vocabulary": self.name})]
        return self.references

    def get_labels_by_lang(self, lang):
        return [r.get(f"name_{lang}") for r in self.references]

    def set_standards(self, standards):
        self.standards = standards
        return self.standards
