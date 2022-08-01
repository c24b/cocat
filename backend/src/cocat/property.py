"""
Property

parameters to build model
"""

import datetime
import json
import logging
from collections import defaultdict
import os
from typing import Optional, Any, Union
from pydantic import BaseModel, validator, root_validator, constr

from cocat.vocabulary import Vocabulary
# from cocat.model import Model
from pydantic.dataclasses import dataclass


LOGGER = logging.getLogger(__name__)


class Property(BaseModel):
    """
    A class to parse and declare metadata properties of a Model

    Attributes
    ----------
    created_date: datetime.date
        day of creation of the property YYYY-MM-dd
    updated_date: datetime date
        day of the property's last update YYYY-MM-dd
    model: str
        name of the model
    field: str
        name of the field
    default_lang: str
        Lang in wich fields are displayed : accepted 'en' or 'fr'. default to 'fr'. 
    description: str
        description of the field. Help Message for enduser in default_lang
    multilang: bool
        is the value need to be available in both language: fr and en and translated? 
    datatype: str
        type of the value: accepted datatype are string integer boolean, date, datetime, object. 
        In particular case like date and datetime: format indicates the required format of date. 
        For string we can add additional pydantic supported type: email, url
    format: str 
        additional type checking for field: range
    constraint: str
        additionnal constraint for field unique, min_lenght, max_lenght, ...
    required: bool
        is the field mandatory?
    multiple: bool
        is the fields consists of more than one item?
    full_text_search: bool
        activate the full search text on this field 
    filter: bool
        activate the filter on this field
    is_external_model: bool
        does the field is a reference to another model?
    external_model_name: str
        if is_external_model provides the name of the model mapped with the field
    external_model_keys: list
        if is_external_model: foreign keys mapping with the external model
    is_vocabulary: bool
        does the field is a reference to a controled vocabulary?
    vocabulary_name: str
        if is_vocabulary specify the name of the vocabulary used
    vocabulary_filename: str
        if is_vocabulary  and vocabulary doesnt exists already specify the filename to store it
    dcat_label: str
        if is_vocabulary and vocabulary respects a dcat ap standard provides the corresponding label
    inspire_label: str
        if is_vocabulary has a corresponding label in INSPIRE provides the label
    labels: list
        when vocabulary exists or have been initialized provides the enumeration of labels of the vocabulary in english to be exported in xml
    references: list
        when vocabulary exists or have been initialized provides the enumeration of labels of the vocabulary in the default lang for enduser
    uris: list
        when vocabulary exists or have been initialized provides the enumeration of uris of the vocabulary in the default lang
    example: str
        example of the value expected used in API as demo
    default: str
        default value expected if not specified can be used as a proposal for enduser and as default value at model generation.

    Methods
    -------
    datatype_to_pytype
    export

    Properties
    -------
    
    mapping
    py
    json
    json_schema:
    xml

    """
    created_date: datetime.date = datetime.date.today()
    updated_date: datetime.date = datetime.date.today()
    model: str 
    field: str 
    default_lang: str = "fr"
    multilang: bool = False
    datatype: str = "string"
    format: Optional[str] = None
    constraint: Optional[str] = None
    required: bool = True
    multiple: bool = False
    search_full_text: bool = False
    filter_values: bool = False
    is_external_model: bool = False
    external_model_name: Optional[str]
    external_model_keys: Optional[list]
    is_vocabulary: Optional[bool] = False
    vocabulary_name: Optional[str] = None 
    filename: Optional[str] = None
    dcat_label: Optional[str]
    inspire_label: Optional[str]
    labels: Optional[list]
    references: Optional[list]
    uris: Optional[list]
    name: Optional[str]
    description: Optional[str]
    example: Optional[str]
    default: Optional[str]
    
    @validator("external_model_keys", pre=True)
    def cast_2_list(cls, value):
        if not isinstance(value, list):
            return value.split("|")
        return value
    
    @validator("created_date", "updated_date", pre=True)
    def check_date_format(cls, value):
        return datetime.datetime.strptime(
            value,
            "%d/%m/%Y"
        ).date()

    @validator("field", "model", pre=True, allow_reuse=True)
    def snake_case(cls, value):
        tmp = ""
        for c in value.lower():
            if c.isalnum:
                tmp += c
            else:
                tmp += "_"    
        return tmp

    @validator("default_lang", pre=True)
    def check_lang_is_supported(cls, value, values):
        # supported_languages = {"fr": "en", "en": "fr"} 
        if value not in ["en", "fr"]:
        # if value not in list(supported_languages.keys()):
            raise ValueError(
                    f"Lang {value} is not supported. Languages supported are French (default) fr and English en")
        # values["other_lang"] = supported_languages[value]
        return value

    
    @validator(
        "model",
        "field",
        "datatype",
        "external_model_name",
        "vocabulary_name",
        "filename",
        "dcat_label",
        "inspire_label",
        "example",
        "default",
        "external_model_keys",
        "labels",
        "references",
        "uris",
        pre=True,
        allow_reuse=True,
    )
    def strip_str(cls, value):
        """strip string"""
        if value is None:
            return value
        if isinstance(value, list):
            return [v.strip() for v in value]
        return value.strip()
    @validator("model",
        "field",
        "datatype",
        "external_model_name",
        "vocabulary_name",
        "filename",
        "dcat_label",
        "inspire_label",
        "example",
        "default",
        "external_model_keys",
        "labels",
        "references",
        "uris",
        pre=True,
        allow_reuse=True)
    def if_empty_set_to_none(cls, value):
        """set empty string to None"""
        if value == "":
            return None
        else:
            return value

    @validator(    
        "multilang",
        "required",
        "multiple",
        "search_full_text",
        "filter_values", 
        "is_external_model",
        "is_vocabulary",
        pre=True, allow_reuse=True)
    def cast_2_bool(cls, value):
        """set string representation of bool into bool"""
        if value in ["true", "True", 1]:
            return True
        if value in ["false", "False", 0]:
            return False
        return bool(value)

    @validator("datatype", pre=True)
    def check_supported_datatype(cls, value):
        """check datatype"""
        accepted_datatypes = [
            "string",
            "integer",
            "object",
            "date",
            "datetime",
            "integer",
            "boolean",
        ]
        if value not in accepted_datatypes:
            raise ValueError(f"datatype must be in {accepted_datatypes}")
        return value
    
    
    @root_validator
    def check_external_model(cls, values):
        if values["is_external_model"] is True:
            if values["external_model_name"] is None and values["external_model_keys"] is None:
                raise ValueError(
                        f"Field is declared as an external model reference. Set external_model_name and external_model_keys"
                    )
            elif values["external_model_name"] is None:
                raise ValueError(
                        f"Field is declared as an external model reference. Set external_model_name "
                    )
            elif values["external_model_keys"] is None:
                raise ValueError(
                        f"Field is declared as an external model reference. Set external_model_keys "
                    )
        return values

    @root_validator
    def check_vocabulary(cls, values):
        if values["is_vocabulary"] is True:
            if values["vocabulary_name"] is not None:
                if values["filename"] is None: 
                # and values["references"] is None:
                    raise ValueError(
                        f"Field is declared as a vocabulary: vocabulary as to be initialized throuoght a csv file or a set of references. Set `filename` or references."
                    )
                else:
                    filename = os.path.join(os.path.dirname(__file__), values["filename"])
                    if  os.path.isfile(filename) is False:
                        raise ValueError(
                            f"File not found error: `{filename}`."
                        )
                    v = Vocabulary(name=values["vocabulary_name"], csv_file=values["filename"])
                    values["labels"] = v.labels
                    values["references"] = v.get_labels_by_lang(values["default_lang"])
                    values["uris"] = v.uris
                    return values
            else:
                raise ValueError("Field is declared as a vocabulary and no vocabulary name has been provided. Set `vocabulary_name` ")
        else:
            if values["vocabulary_name"] is not None:
                raise ValueError("Field has a vocabulary name and is not declared as a vocabulary. Set `is_vocabulary` to True. ")
        return values
    
    @root_validator
    def check_full_text_search(cls, values):
        if values["search_full_text"] is True:
            if values["datatype"] not in ["string", "object"]:
                raise ValueError("Full text search can't be activated for this datatype. Must be a string or an external_model")
        return values
    
    @root_validator
    def check_filter_values(cls, values):
        if values["filter_values"] is True:
            if values["is_external_model"] is False and values["is_vocabulary"] is False and values["datatype"] == "string":
                raise ValueError("Filter can't be activated for this field: field should not consists of free text")
        return values
    # @property
    # def index_mapping(self, lang):
    #     """given type and lang returns mapping properties for index"""
    #     if lang == "fr":
    #         analyzer = "std_french"
    #     else:
    #         analyzer = "std_english"
    #     if self.search or self.filter:
    #         if self.external_model_name == "vocabulary":
    #             return {
    #                 "type": "text",
    #                 "fields": {"raw": {"type": "keyword"}},
    #                 "analyzer": analyzer,
    #             }
    #         if self.external_model_name is not None:
    #             return {"type": "nested"}
    #         if self.datatype == "string":
    #             return {
    #                 "type": "text",
    #                 "fields": {"raw": {"type": "keyword"}},
    #                 "analyzer": analyzer,
    #             }
    #         if self.datatype == "date":
    #             if self.constraint == "range":
    #                 return {"type": "integer_date"}

    #             else:
    #                 return {"type": "date", "format": "yyyy-MM-dd||yyyy/MM/dd"}

    #         if self.datatype == "datetime":
    #             if self.constraint == "range":
    #                 return {"type": "integer_date"}
    #             else:
    #                 return {
    #                     "type": "date",
    #                     "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time_nanos",
    #                 }
    #         if self.datatype == "boolean":
    #             return {"type": self.datatype}

    #         if self.datatype == "integer":
    #             if self.constraint == "range":
    #                 return {"type": "integer_range"}
    #             else:
    #                 return {"type": self.datatype}
    #         else:
    #             return {
    #                 "type": "text",
    #                 "fields": {"raw": {"type": "keyword"}},
    #                 "analyzer": analyzer,
    #             }

    # def py(self):
    #     """pydantic reprsentation of a Dataclass property declaration"""
    #     py_type = self.datatype_to_pytype().__name__
    #     if py_type == "dict" and self.external_model_name is not None:
    #         py_type = self.external_model_name.title()
    #     if not self.required:
    #         line = f"{self.field}: Optional"
    #         if self.multiple:
    #             line += f"[List[{py_type}]]"
    #         else:
    #             line += f"[{py_type}]"
    #     else:
    #         if self.multiple:
    #             line = f"{self.field}: List[{py_type}]"
    #         else:
    #             line = f"{self.field}: {py_type}"
    #     # not implemented yet: need to cast and check default first and to set a default_lang
    #     # default = getattr(self, f"default_{lang}")
    #     # if default is not None or default != "":
    #     #     if self.multiple:
    #     #         line += f"= [{default}]"
    #     #     else:
    #     #         line += f"= {default}"
    #     if self.multiple:
    #         line += f"= []"
    #     else:
    #         line += f"= None"
    #     return line

    
    # def example_by_lang(self, lang):
    #     """
    #     Build the example : {"field": "example"}
    #     in the corresponding language"""
    #     if lang not in ["fr", "en"]:
    #         raise ValueError(f"Language {lang} is not supported.")
    #     return {self.field: getattr(self, f"example_{lang}")}

    # def example(self):
    #     """
    #     Build the example : {"field": {"fr": "example_fr", "en": "example_en"}}
    #     """
    #     return {self.field: {"fr": self.example_fr, "en": self.example_en}}

    # def default_by_lang(self, lang):
    #     """
    #     Build the example for model: {"field": "example"}
    #     in the corresponding language"""
    #     if lang not in ["fr", "en"]:
    #         raise ValueError(f"Language {lang} is not supported.")
    #     return {self.field: getattr(self, f"default_{lang}")}

    # def default(self):
    #     """
    #     Automatically build the field with the example: {"field": {"fr": "example_fr", "en": "example_en"}}
    #     """
    #     return {self.field: {"fr": self.default_fr, "en": self.default_en}}

    # def field_by_lang(self, lang):
    #     """Set the field in the corresponding language"""
    #     if lang not in ["fr", "en"]:
    #         raise ValueError(f"Language {lang} is not supported.")
    #     if self.field.endswith(lang):
    #         return self.field.split("_")[0]
    #     else:
    #         return self.field

    # def json(self):
    #     return {
    #         self.field: {
    #             "type": self.datatype,
    #             "required": self.required,
    #             "format": self.format,
    #             "constraint": self.constraint,
    #         }
    #     }

    # def json_schema(self):
    #     return {
    #         self.field: {
    #             "type": self.datatype,
    #             "description": self.description_en,
    #             "required": self.required,
    #             "format": self.format,
    #             "constraint": self.constraint,
    #         }
    #     }

    # def pytype(self):
    #     if self.datatype == "string":
    #         if self.format == "email":
    #             return "EmailStr"
    #         if self.format == "url":
    #             return "HttpUrl"
    #         return "str"
    #     if self.datatype == "integer":
    #         return "int"
    #     if self.datatype == "boolean":
    #         return "bool"
    #     if self.datatype == "date":
    #         return "datetime.date"
    #     if self.datatype == "date":
    #         return "datetime.datetime"
    #     if self.datatype == "object":
    #         return "dict"
    #     else:
    #         return "str"

    # # @property
    # # def csv(self):
    # #     if self.multiple:
    # #         value = value.split("|")
    # #     if self.datatype == "string":
    # #         return str(value)
    # #     elif self.datatype == "date":
    # #         return datetime.datetime.strftime(value, self.format)
    # #     elif self.datatype == "datetime":
    # #         return datetime.datetime.strftime(value, self.format)
    # #     else:
    # #         return str

    # # @property
    # # def dcat(self, value):
    # #     if self.vocabulary_label is not None:
    # #         return f"<{self.vocabulary_label}></{self.vocabulary_label}>"
    # #     return None
    # def datatype_to_pytype(self):
    #     """cast declared datatype (javascript notation) into native python type"""
    #     if self.datatype == "date":
    #         return datetime.date
    #     if self.datatype == "datetime":
    #         return datetime.datetime
    #     if self.datatype == "string":
    #         return str
    #     if self.datatype == "integer":
    #         return int
    #     if self.datatype == "object":
    #         return dict
    #     if self.datatype == "boolean":
    #         return bool
    #     else:
    #         raise ValueError(f"Wrong datatype {self.datatype}")

    # def _export(self, to="csv"):
    #     """Export.

    #     Args:
    #         to(str): the export format
    #             accepted format:
    #         ["csv", "json", "xml", "schema_json", "pydantic", "dcat", "inspire"]
    #     """
    #     accepted_formats = [
    #         "csv",
    #         "json",
    #         "xml",
    #         "schema_json",
    #         "pydantic",
    #         "dcat",
    #         "inspire",
    #     ]
    #     accepted_formats_str = ",".join(accepted_formats)
    #     if not to in accepted_formats:

    #         raise ValueError(f"{to} not in {accepted_formats_str}")
    #     property_d = dict(self.__dict__.items())
    #     if to == "csv":
    #         header = ",".join(list(property_d.keys()))
    #         values = ",".join(list([str(n) for n in property_d.values()]))
    #         return "\n".join([header, values])
    #     elif to == "json":
    #         return json.dumps(property_d)
    #     elif to == "schema_json":
    #         return self.schema_json(indent=2)
    #     # elif to == "xml":
    #     #     return dicttoxml.dicttoxml(property_d)
    #     elif to == "pydantic":
    #         datatype = self._convert("model")
    #         if self.required:
    #             # return f"{self.field}: {datatype} = {self.default_en}"
    #             return f"{self.field}: {datatype}"
    #         else:
    #             # return f"{self.field}: Optional[{datatype}] = {self.default_en}"
    #             return f"{self.field}: Optional[{datatype}]"

    # def _convert(self, to="pydantic_str", value=None):
    #     if to == "model":
    #         if self.datatype == "string":
    #             if self.format == "email":
    #                 return "EmailStr"
    #             if self.format == "url":
    #                 return "HttpUrl"
    #             return "str"
    #         if self.datatype == "integer":
    #             return "int"
    #         if self.datatype == "boolean":
    #             return "bool"
    #         if self.datatype == "date":
    #             return "datetime.date"
    #         if self.datatype == "date":
    #             return "datetime.datetime"
    #         if self.datatype == "object":
    #             return "dict"
    #         else:
    #             return "str"
    #     elif to == "python":
    #         if self.datatype == "string":
    #             return str(value)
    #         if self.datatype == "integer":
    #             return int(value)
    #         if self.datatype == "boolean":
    #             return bool(value)
    #         if self.datatype == "date":
    #             return datetime.datetime.strftime(value, self.format)
    #         if self.datatype == "object":
    #             return dict(value)
    #         else:
    #             return str(value)
    #     elif to == "csv":
    #         if self.multiple:
    #             value = value.split("|")
    #         if self.datatype == "string":
    #             return str(value)
    #         elif self.datatype == "date":
    #             return datetime.datetime.strftime(value, self.format)
    #         elif self.datatype == "datetime":
    #             return datetime.datetime.strftime(value, self.format)
    #         else:
    #             return str
    #     elif to == "dcat":
    #         if self.vocabulary_label is not None:
    #             if value is not None:
    #                 return f"<{self.vocabulary_label}>{value}</{self.vocabulary_label}>"
    #         return
    #     elif to == "inspire":
    #         return f"<{self.inspire}>{value}</{self.vocabulary_label}>"
    #     elif to == "dict":
    #         if self.multiple:
    #             # if self.is_controled:
    #             #     if self.constraint == "oneof":
    #             return {self.field: value.split("|")}
    #         else:
    #             return {self.field: value}
