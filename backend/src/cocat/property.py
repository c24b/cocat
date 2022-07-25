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

LOGGER = logging.getLogger(__name__)

class Property(BaseModel):
    """
    A class to parse metadata properties out of a Rule


    Attributes
    ----------
    lang: str
        default to 'fr'. Lang for fields relative to lang en or fr
    issue_date: datetime.date
        date of creation of the property YYYY-MM-dd
    model: str
        name of the model
    field: str
        name of the field
    name_fr : str
        name of the field as displayed
    external_model_name: Optional[str]
        name of the model the field is a reference to
    external_model_display_keys: Optional[list]
        list of the foreign key for the external model
    vocabulary_name: Optional[str]
        name of the vocabulary table that stores all the possible references
    vocabulary_filename: Optional[str]
        csv_file that stores the vocabulary
    vocabulary_label: Optional[str]
        string representation of the xml label of external vocabulary
    inspire: Optional[str]
        string representation of the inspire label
    translation: bool = False
        translate the value of the field if missing in other lang
    multiple: bool = None
        field accepts n values
    datatype: str = "string"
        type notation of the field using javascript notation.
        accepted_datatypes = ["string","integer","object","date","datetime","integer","boolean"]
        that determines the type property of the model for the validation, the insertion and the indexation
    format: Optional[str]
        additionnal information for the type such as expected date format or specific string representation (email, url...)
    constraint: Optional[str]
        string representation of a constraint for json model or database check
    search: bool
        define if the field is indexed in full text and available in search engine
    filter: bool
        define if the field is available to filter options
    required: bool
        define if the field is mandatory
    name_fr: str
        name as displayed in the french interface
    name_en: Optional[str] = ""
        name as displayed in the english interface
    description_fr: Optional[str] = ""
        description of the field as displayed in the french interface: more informations
    description_en: Optional[str] = ""
        description of the field as displayed in the english interface: more informations
    example_fr: Optional[str] = None
        example value in french
    example_en: Optional[str] = None
        example value in english
    default_fr: Optional[str] = None
        default value in french can be used as help text or template during insertion
    default_en: Optional[str] = None
        default value in english can be used as help text or template during insertion
    comment: Optional[str] = None
        a comment on the status of the field


    Methods
    -------

    datatype_to_pytype: str
        use datatype to cast datatype from json notation to pydantic notation. Only [string, int, bool, dict] are acepted

    _convert:

    _export:

    Properties
    -------
    is_vocabulary:

    vocabulary:

    labels:

    labels_by_lang:

    is_external_model:

    external_model:

    mapping:

    display:

    example_by_lang:
    example
    default_by_lang:
    default:
    field_by_lang:
    py:

    json:
    json_schema:
    model:
    """
    lang: Optional[str] = "fr"
    issue_date: datetime.date = datetime.date.today()
    model: str = None
    field: str = None
    lang: str = "fr"
    external_model: Optional[str] 
    external_model_name: Optional[Union[str, None]] 
    external_model_display_keys: Optional[list] = ["id", "name"]
    is_external_model: Optional[bool] = False
    vocabulary_name: Optional[str] 
    is_vocabulary: Optional[bool] = False
    vocabulary_filename: Optional[str]
    vocabulary_label: Optional[str] = None
    labels: Optional[list]
    inspire: Optional[str] = None
    translation: bool = False
    multiple: bool = False
    datatype: str = "string"
    format: Optional[str] = None
    constraint: Optional[str] = None
    search: bool = False
    is_searchable: Optional[bool]
    filter: bool = False
    has_filter: Optional[bool]
    required: bool = True
    name_fr: str
    name_en: Optional[str]
    description_fr: Optional[str]
    description_en: Optional[str]
    example_fr: Optional[str] = None
    example_en: Optional[str] = None
    default_fr: Optional[str] = None
    default_en: Optional[str] = None
    comment: Optional[str] = None
    
    @validator(
        "external_model_name",
        "external_model_display_keys",
        "vocabulary_name",
        "vocabulary_filename",
        "vocabulary_label",
        "inspire",
        "name_en",
        pre=True,
        allow_reuse=True,
    )
    def strip(cls, value):
        if value is None:
            return value
        if isinstance(value, list):
            return [v.strip() for v in value]
        return value.strip()

    @validator(
        "external_model_name",
        "external_model_display_keys",
        "vocabulary_name",
        "vocabulary_filename",
        "vocabulary_label",
        "inspire",
        "name_en",
        "name_fr",
        "description_en",
        "description_fr",
        pre=True,
        allow_reuse=True,
    )
    def if_empty_set_to_none(cls, value):
        """set empty string to None"""
        if value == "":
            return None
        else:
            return value

    @validator(
        "search",
        "filter",
        "required",
        "multiple",
        "translation",
        "is_external_model",
        "is_vocabulary",
        "is_searchable",
        "has_filter",
        pre=True)
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
    
    @validator("lang", pre=True)
    def check_lang_is_supported(cls, value):
        if value not in ["fr", "en"]:
            raise ValueError(
                    f"Lang {value} is not supported. Languages supported are French (default) fr and English en")
        return value
    @validator("external_model_name", pre=True)
    def set_is_external_model(cls, external_model_name, values):
        if external_model_name is not None:
            if external_model_name != "vocabulary":
                values["is_external_model"] = True
                return values
        else:
            values["is_external_model"] = False
            return values
    
    @validator("vocabulary_name", pre=True, allow_reuse=True)
    def set_vocabulary_name(cls, value, values):
        if value is not None and values["external_model_name"] == "vocabulary":
            values["is_vocabulary"] = True
            
        else:
            values["is_vocabulary"] = False
            
        if value is None and values["external_model_name"] == "vocabulary":
            raise ValueError(
                    f"Vocabulary name is not declared but external_model_name is set to Vocabulary"
                )
        elif value is None and values["vocabulary_filename"] is not None:
            raise ValueError(
                    f"Vocabulary name is not declared but external_file is declared"
                )
        # else:
            # if values["vocabulary_filename"] is not None:
            #     v = Vocabulary(value, csv_file= values["vocabulary_filename"])
            #     values["labels"] = v.labels   
            # else:
            #     v = Vocabulary(value)
            #     values["labels"] = v.labels
        return values
          
    @validator("vocabulary_filename")
    def check_voc_name_with_filename(cls, value, values):
        # value  = values["vocabulary_filename"]
        value = os.path.join(os.path.dirname(__file__), value)
        if  os.path.isfile(value) is False:
            raise ValueError(
                f"File not found error: `{value}`."
                )    
        else:
            v = Vocabulary(values["vocabulary_name"], csv_file= value)
            values["labels"] = v.labels   
        return values
   
            
    
    @validator("vocabulary_name", pre=True)
    def check_is_vocabulary(cls, value, values):
        if value is not None and values["external_model_name"] == "vocabulary":
            values["is_vocabulary"] = True
        else:
            values["is_vocabulary"] = False
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
