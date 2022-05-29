"""
Rule

parameters to build model
"""

import datetime
import json
from csv import DictReader
import dicttoxml
from typing import Optional
from pydantic import BaseModel, validator



def cast_to_pytype(value, datatype):
    '''cast value with declared datatype (javascript notation) into native python type'''
    try:
        return datatype_to_pytype(datatype)(value)
    except TypeError as e:
        print(e)
        return value
    except Exception as e:
        print(e)
        return value

class Rule(BaseModel):
    """
    A class to represent a Rule

    ...

    Attributes
    ----------
    field: str
        name of the field
    name_fr : str
       Display  name of the field

    Methods
    -------
    

    """
    issue_date: datetime.date = datetime.date.today()
    model: str
    field: str
    external_model_name: Optional[str] = None
    external_model_display_keys: Optional[list] = None
    reference_table: Optional[str]
    vocab: Optional[str] = None
    inspire: Optional[str] = None
    translation: bool = False
    multiple: bool = None
    datatype: str = "string"
    format: Optional[str] = None
    constraint: Optional[str] = None
    search: bool = False
    filter: bool = False
    required: bool = True
    admin_display_order: int = 1
    list_display_order: int = -1 
    item_display_order: int = -1 
    name_fr: str
    name_en: Optional[str] = ""
    description_fr: Optional[str] = ""
    description_en: Optional[str] = ""
    example_fr: Optional[str] = None
    example_en: Optional[str] = None
    default_fr: Optional[str] = None
    default_en: Optional[str] = None
    comment: Optional[str] = None

    @validator("external_model_name", "external_model_display_keys", "reference_table","format", "constraint", "vocab", "inspire", pre=True, allow_reuse=True)
    def if_empty_set_to_none(cls, value):
        """set empty string to None """
        if value == "":
            return None
        else:
            return value
    
    @validator("search", "filter", "required", "multiple", "translation", pre=True, allow_reuse=True)
    def cast_2_bool(cls, value):
        """ set string representaton of bool into bool"""
        if value in ["true", "True", 1]:
            return True
        if value in ["false", "False", 0]:
            return False
        return bool(value)
    
    @validator("admin_display_order", "list_display_order", "item_display_order", pre=True)
    def cast_2_int(cls, value):
        return int(value)
    
    
    @validator("external_model_display_keys", pre=True)
    def parse_external_model_display_keys(cls, value, values):
        if value is not None:
            if values["external_model_name"] is None:
                raise ValueError("As external_model keys are declared, external model should be specified")
            else:
                return value.split("|")
        return value
    
    # @validator("example_fr", "example_en", "default_fr", "default_en", pre=True)
    # def validate_datatype_example(cls, value, values):
    #     """cast example and default with the declared datatype"""
        
    #     field = values["field"]
    #     datatype = values["datatype"]
    #     is_multiple = values["multiple"]
    #     if value is None:
    #         if is_multiple:
    #             return [None]
    #         return value    
    #     if is_multiple:
    #         return [cast_to_pytype(v, datatype) for v in value.split('|')]
    #     else:
    #         return cast_to_pytype(value, datatype)

    @validator("reference_table", pre=True)
    def check_reference(cls, value, values):
        ext_model = values["external_model_name"]
        if value is not None:
            if ext_model is None:
                return "reference"
        return value
    

    @validator("external_model_name")
    def check_external_model(cls, value, values, **kwargs):
        field = values["field"]
        if 'reference_table' in values:
            reference_table = values["reference_table"]
        
            if reference_table is not None and value is None:
                return "reference"
        return value
    
    @validator("external_model_display_keys")
    def check_external_model_keys(cls, value, values):
        field = values["field"]
        ext_model = values["external_model_name"]
        if ext_model is not None:
            if value is None:
                raise ValueError(
                    f"{field} has external_model_name specified and no display keys declared. Set external_model_display_keys"
                )
        return value

    @validator("admin_display_order")
    def check_view_order(cls, value, values):
        field = values["field"]
        if value == 0 or value == -1:
            raise ValueError(f"{field} must be display set an order > 0")
        return value
            
    @validator("datatype", pre=True, allow_reuse=True)
    def check_supported_datatype(cls, value):
        """check"""
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

    @validator("search")
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
    
    @validator("filter")
    def check_filter_option(cls, filter, values):
        """field can be filter only if its not a free text"""
        field = values["field"]
        if filter:
            if values["external_model_name"] is  None and values["datatype"] == "string":
                raise ValueError(
                    f"{field} can't be filtered as it consists of a free text: not a reference, not and external model or a type can be filter int, date, ..."
                )
        return filter
    
    def datatype_to_pytype(self):
        '''cast declared datatype (javascript notation) into native python type'''
        if self.datatype == "date":
            return datetime.date
        if self.datatype == "datetime":
            return datetime.datetime
        if self.datatype == "string":
            return str
        if self.datatype == "integer":
            return int
        if self.datatype == "object":
            return dict
        if self.datatype == "boolean":
            return bool
    

    def get_index_properties(self, lang):
        """prepare for mapping """
        if lang == "fr":
            analyzer = "std_french"
        else:
            analyzer = "std_english"
        if self.search or self.filter:
            if self.external_model_name == "reference":
                return {"type": "text", "fields": {"raw": {"type": "keyword"}}, "analyzer": analyzer}
            if self.external_model_name is not None:
                return {"type": "nested"}
            if self.datatype == "string":
                return {"type": "text", "fields": {"raw": {"type": "keyword"}}, "analyzer": analyzer}
            if self.datatype == "date":
                if self.constraint == "range":
                    return {"type": "integer_date"}
                    
                else:
                    return {"type": "date", "format": "yyyy-MM-dd||yyyy/MM/dd"}
            
            if self.datatype == "datetime":
                if self.constraint == "range":
                    return {"type": "integer_date"}
                else:
                    return {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time_nanos"}
            if self.datatype == "boolean":
                return {"type": self.datatype}
                
            if self.datatype == "integer":
                if self.constraint == "range":
                    return {"type": "integer_range"}
                else:
                    return {"type": self.datatype}
            else:
                return {"type": "text", "fields": {"raw": {"type": "keyword"}}, "analyzer": analyzer}

    def build_model_property(self, lang):
        """Build Dataclass field line for pydantic model"""
        py_type = self.datatype_to_pytype().__name__
        if py_type == "dict" and self.external_model_name is not None:
            py_type  = self.external_model_name.title()
        if not self.required:
            line = f"{self.field}: Optional"
            if self.multiple:
                line += f"[List[{py_type}]]"
            else:
                line += f"[{py_type}]"
        else:
            if self.multiple:
                line = f"{self.field}: List[{py_type}]"
            else:
                line = f"{self.field}: {py_type}"
        #not implemented yet
        # default = getattr(self, f"default_{lang}")
        # if default is not None or default != "":
        #     if self.multiple:
        #         line += f"= [{default}]"
        #     else:
        #         line += f"= {default}"
        if self.multiple:
            line += f"= []"
        else:
            line += f"= None"
        return line

    def get_display_options_by_lang(self, lang):
        """return only the options in the desired language"""
        if lang not in ["fr", "en"]:
            raise ValueError(f"Language {lang} is not supported.")
        keys = [
            f"name_{lang}",
            f"section_name_display_{lang}",
            f"section_order",
            f"section_name_{lang}",
            f"description_{lang}",
            "admin",
            "list",
            "item",
        ]
        return {k: v for k, v in self.__dict__.items() if k in keys}

    def build_example_by_lang(self, lang):
        """
        Automatically build the field with the example: {"field": "example"} 
        in the corresponding language"""
        if lang not in ["fr", "en"]:
            raise ValueError(f"Language {lang} is not supported.")
        return {self.field: getattr(self, f"example_{lang}")}

    def build_example(self):
        """
        Automatically build the field with the example: {"field": {"fr": "example_fr", "en": "example_en"}} 
        """
        return {self.field: {"fr": self.example_fr, "en": self.example_en}}
    def build_default_by_lang(self, lang):
        """
        Automatically build the field with the example: {"field": "example"} 
        in the corresponding language"""
        if lang not in ["fr", "en"]:
            raise ValueError(f"Language {lang} is not supported.")
        return {self.field: getattr(self, f"default_{lang}")}

    def build_default(self):
        """
        Automatically build the field with the example: {"field": {"fr": "example_fr", "en": "example_en"}} 
        """
        return {self.field: {"fr": self.default_fr, "en": self.default_en}}
    
    def get_by_lang(self, lang):
        """Set the rule in the corresponding language"""
        if lang not in ["fr", "en"]:
            raise ValueError(f"Language {lang} is not supported.")
        dict_by_lang = {}
        for k, v in self.__dict__.items():
            if k.endswith(lang):
                dict_by_lang[k.split("_")[0]] = v
            else:
                dict_by_lang[k] = v
        setattr(self, f"_{lang}", dict_by_lang)

    def _export(self, to="csv"):
        """Export.

        Args:
            to(str): the export format
                accepted format:
            ["csv", "json", "xml", "schema_json", "pydantic", "dcat", "inspire"]
        """
        accepted_formats = [
            "csv",
            "json",
            "xml",
            "schema_json",
            "pydantic",
            "dcat",
            "inspire",
        ]
        accepted_formats_str = ",".join(accepted_formats)
        if not to in accepted_formats:

            raise ValueError(f"{to} not in {accepted_formats_str}")
        rule_d = dict(self.__dict__.items())
        if to == "csv":
            header = ",".join(list(rule_d.keys()))
            values = ",".join(list([str(n) for n in rule_d.values()]))
            return "\n".join([header, values])
        elif to == "json":
            return json.dumps(rule_d)
        elif to == "schema_json":
            return self.schema_json(indent=2)
        elif to == "xml":
            return dicttoxml.dicttoxml(rule_d)
        elif to == "pydantic":
            datatype = self._convert("model")
            if self.required:
                # return f"{self.field}: {datatype} = {self.default_en}"
                return f"{self.field}: {datatype}"
            else:
                # return f"{self.field}: Optional[{datatype}] = {self.default_en}"
                return f"{self.field}: Optional[{datatype}]"

    def _convert(self, to="pydantic_str", value=None):
        if to == "model":
            if self.datatype == "string":
                if self.format == "email":
                    return "EmailStr"
                if self.format == "url":
                    return "HttpUrl"
                return "str"
            if self.datatype == "integer":
                return "int"
            if self.datatype == "boolean":
                return "bool"
            if self.datatype == "date":
                return "datetime.date"
            if self.datatype == "date":
                return "datetime.datetime"
            if self.datatype == "object":
                return "dict"
            else:
                return "str"
        elif to == "python":
            if self.datatype == "string":
                return str(value)
            if self.datatype == "integer":
                return int(value)
            if self.datatype == "boolean":
                return bool(value)
            if self.datatype == "date":
                return datetime.datetime.strftime(value, self.format)
            if self.datatype == "object":
                return dict(value)
            else:
                return str(value)
        elif to == "csv":
            if self.multiple:
                value = value.split("|")
            if self.datatype == "string":
                return str(value)
            elif self.datatype == "date":
                return datetime.datetime.strftime(value, self.format)
            elif self.datatype == "datetime":
                return datetime.datetime.strftime(value, self.format)
            else:
                return str
        elif to == "dcat":
            if self.vocab is not None:
                if value is not None:
                    return f"<{self.vocab}>{value}</{self.vocab}>"
            return
        elif to == "inspire":
            return f"<{self.inspire}>{value}</{self.vocab}>"
        elif to == "dict":
            if self.multiple:
                # if self.is_controled:
                #     if self.constraint == "oneof":
                return {self.field: value.split("|")}
            else:
                return {self.field: value}

    # class Config:
    #     json_encoders = {
    #         # custom output conversion for datetime
    #         datetime.date: convert_date_to_str
    #     }


class CSVRuleImporter:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.rules = []
        self.set_rules()

    def set_rules(self):
        with open(self.csv_file, "r") as f:
            reader = DictReader(f, delimiter=",")
            for row in reader:
                r = Rule.parse_obj(row)
                self.rules.append(r)
