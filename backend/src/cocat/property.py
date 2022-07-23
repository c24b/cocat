"""
Property

parameters to build model
"""

import datetime
import json
import logging
from collections import defaultdict
import os
from typing import Optional, Any
from pydantic import BaseModel, validator, root_validator, constr

from cocat.vocabulary import Vocabulary
# from cocat.model import Model

LOGGER = logging.getLogger(__name__)

class Property(BaseModel):
    """
    A class to parse metadata properties out of a Rule


    Attributes
    ----------
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

    issue_date: datetime.date = datetime.date.today()
    model: str = None
    field: str = None
    lang: str = "fr"
    external_model_name: Optional[str] = None
    external_model_display_keys: Optional[list] = None
    vocabulary_name: Optional[str] = None
    vocabulary_filename: Optional[str] = None
    vocabulary_label: Optional[str] = None
    inspire: Optional[str] = None
    translation: bool = False
    multiple: bool = False
    datatype: str = "string"
    format: Optional[str] = None
    constraint: Optional[str] = None
    search: bool = False
    filter: bool = False
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
    is_vocabulary: Optional[bool]
    # vocabulary: Optional[list] = None

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
    
    # @validator("lang", pre=True)
    # def check_lang_is_supported(cls, value, values):
    #     LOGGER.warning(values)
    #     if value not in ["fr", "en"]:
    #         raise ValueError(
    #                 f"Lang {value} is not supported. Languages supported are French (default) fr and English en")
    #     return value
    @validator("search", pre=True)
    def check_search_option(cls, search, values):
        """search must be a text or a nested object to be indexed"""
        datatype = values["datatype"]
        field = values["field"]
        if search is True:
            if datatype not in ["string", "object"]:
                raise ValueError(
                    f"{field} search option is set to {search}, it can't be index in full text: invalid {datatype}. Set search option to False"
                )
        return search

    @validator("filter", pre=True)
    def check_filter_option(cls, filter, values):
        """field can be filter only if its not a free text"""
        field = values["field"]
        if filter:
            if values["external_model_name"] is None and values["vocabulary_name"] is None and values["datatype"] == "string":
                raise ValueError(
                    f"{field} can't be filtered as it consists of a free text . Filter should be executed on a following datatype: an integer, date range or on an external_model value or on vocabulary labels"
                )
        return filter

    # @validator("vocabulary_name", pre=True)
    # def check_reference(cls, value, values):
    #     ext_model = values["external_model_name"]
    #     if value is not None:
    #         if ext_model is None:
    #             return "vocabulary"
    #     return value
    
    @validator("vocabulary_filename")
    def check_vocabulary_filename(cls, value, values):
        voc_name = values["vocabulary_name"]
        if value is not None:
            if voc_name is None:
                raise ValueError(
                    f"As a filename for vocabulary {value} is declared, a name for the vocabulary should be specified"
                )
            if not value.endswith(".csv"):
                return os.path.abspath(value + ".csv")
            else:
                return os.path.abspath(value)
        return value

    # @root_validator(pre=False)
    # def check_external_model(cls, value, values, **kwargs):
    #     field = values["field"]
    #     if "vocabulary_name" in values:
    #         vocabulary_name = values["vocabulary_name"]

    #         if vocabulary_name is not None and value is None:
    #             values["vocabulary_name"] = "vocabulary"
    #     return values
    
    @root_validator(pre=False)
    def set_vocabulary(cls,values) -> dict:
        if values["vocabulary_name"] is not None and values["external_model_name"] == "vocabulary": 
            values["is_vocabulary"] = True
            # if values["vocabulary_filename"] is not None:
                # values["vocabulary"] = Vocabulary(values["vocabulary_name"], csv_file=["vocabulary_filename"]).get_labels()
        else:
            values["is_vocabulary"] = False
        return values
        # and self.vocabulary_filename is not None:
    #         self.vocabulary = Vocabulary(name=self.vocabulary_name, csv_file=self.vocabulary_filename)
        return 
    # @root_validator(pre=True)
    # def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     all_required_field_names = {field.alias for field in cls.__fields__.}  # to support alias

    #     extra: Dict[str, Any] = {}
    #     for field_name in list(values):
    #         if field_name not in all_required_field_names:
    #             extra[field_name] = values.pop(field_name)
    #     values['extra'] = extra
    #     return values
    # def set_vocabulary(self):
    #     self.is_vocabulary == 
    #     if self.is_vocabulary and self.vocabulary_filename is not None:
    #         self.vocabulary = Vocabulary(name=self.vocabulary_name, csv_file=self.vocabulary_filename)
    #     return self
    
# class Property(object):
#     def __init__(self, **data) -> None:
#         for k,v in data.items():
#             setattr(self, k, v)
        # self.is_vocabulary = bool(self.vocabulary_name is not None and self.external_model_name == "vocabulary")
    
    # def is_vocabulary(self):
    #     return self.vocabulary_name is not None and self.external_model_name == "vocabulary"
    # def labels(self):
    #     return self.vocabulary.labels

    # def labels_by_lang(self, lang="en"):
    #     return self.vocabulary.get_labels_by_lang(lang)

    # @property
    # def is_external_model(self) -> bool:
    #     return self.external_model_name not in ["vocabulary", None]

    # # @property
    # # def external_model(self) -> object:
    # #     return Model(self.external_model_name, rules=[])
    
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
