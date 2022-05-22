"""
Rule

parameters to build model
"""

import datetime
from typing import Optional
from pydantic import BaseModel, ValidationError, validator

class RulesSetter:
    def __init__(self, dict):
        pass

class RuleSetter:
    """Set rule from str"""

    def __init__(self, item_str):
        self.raw = item_str
        self.set()
    def set(self):
        self.rules = []
        self.matrix = []
        for l in self.raw.split(","):
            if "|" in l:
                self.matrix.append(l.split("|"))

            else:
                self.matrix.append(l)
        for i in self.matrix:
            self.rules.append(Rule(**i))

class Rule(BaseModel):
    """class to  generate, control and check model:
    a rule defines one property of a data model:
    its name, description, example default value
    the model it belongs to and then:
    - display options
    - validation options
    indexation options
    import/export options
    """
    issue_date : str = None
    model: str = None
    field: str = None
    name_fr: str = None
    name_en: Optional[str] = None
    section_name_display_fr: bool = True
    section_name_display_en: bool = True
    section_order: int = None
    section_name_fr: str = None
    section_name_en: Optional[str] = None
    external_model_name: Optional[str] = None
    external_model_display_keys: Optional[list] = None
    is_controled: bool = None
    reference_table: Optional[str] = None
    vocab: Optional[str] = None
    inspire: Optional[str] = None
    translation: bool = None
    multiple: bool = None
    datatype: str = None
    format: str = None
    constraint: str = None
    search: bool = None
    filter: bool = None
    admin: int = None
    list: int = None
    item: int = None
    required: bool = None
    description_fr: str = None
    description_en: Optional[str] = None
    example_fr: str = None
    example_en: Optional[str] = None
    default_fr: str = None
    default_en: Optional[str] = None
    comment: str = None

    def _export(self, to="csv"):
        if to == "csv":
            rules_meta = self.__dict__.items()
            header = ",".join(rules_meta.keys())
            values = "\n".join([",".join(v) for v in rules_meta.values()])
            csv_str = "\n".join([header]+ values) 
            return csv_str
        elif to == "json":
            self.schema_json(indent=2)
        
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
            if self.is_multiple:
                value = value.split("|")
            if self.datatype == "string":
                return str(value)
            elif self.datatype == "date":
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
            if self.is_multiple:
                # if self.is_controled:
                #     if self.constraint == "oneof":
                return {self.field: value.split("|")}
            else:
                return {self.field: value}
    @validator("issue_date", pre=True)
    def parse_date(cls, value):
        if "/" in value:
            format = "%Y/%m/%d"
        elif "-" in value:
            format = "%Y-%m-%d"
        date = datetime.datetime.strptime(
            value,
            "%Y/%m/%d"
        )
        return date.date()
    
    @validator("external_model_display_keys", pre=True)
    def parse_external_model_display_keys(cls, value):
        print(value.split("|"))
        return value.split("|")

    @validator("datatype")
    @classmethod
    def validate_datatype(cls, datatype):
        accepted_datatypes = [
            "string",
            "integer",
            "object",
            "date",
            "datetime"
            "integer",
            "boolean",
        ]
        if datatype not in accepted_datatypes:
            raise ValueError(f"must be in {accepted_datatypes}")
        return datatype

    # @validator(
    #     "search",
    #     "filter",
    #     "external_model_name",
    #     "external_model_display_keys",
    #     "reference_table",
    #     "is_controled",
    #     "admin",
    #     "datatype",
    #     "format",
    #     "constraint"
    # )
    # @classmethod
    # def validate_all_fields_one_by_one(cls, field_value):
    #     # Do the validation instead of printing
    #     print(f"{cls}: Field value {field_value}")
    #     return field_value  # this is the value written to the class field

    @validator("search")
    def check_search_option(cls, field_value, values):
        print("Search", cls, field_value, values)
        datatype = values["datatype"]
        if field_value:
            if datatype not in ["string"]:
                yield ValueError(
                    f"{cls} can't be index in full text. Set search option to False"
                )
                return False
                
        return field_value
    
    @validator("filter")
    def check_filter_option(cls, filter, values):
        datatype = values["datatype"]
        is_reference = values["external_model_name"] == "reference"
        if filter:
            if is_reference is False:    
                if datatype not in ["date", "integer", "boolean"]: 
                    raise ValueError(
                        f"{cls} can't be filtered. Set filter option to False"
                    )    
        return filter

    # @validator("external_model_name", "external_model_display_keys")
    # def check_external_model(cls, field_value, values):
    #     print(values)
    #     if field_value not in ["", "reference"]:
    #         external_model_display_keys = values["external_model_display_keys"]
    #         print(external_model_display_keys)
    #     # if field_value is not None:
    #     #     if external_model_display_keys is None or len(external_model_display_keys) == 0:
    #     #         raise ValueError("{field_value} is an external model. Specify display options")
    #     #     return field_value
    #     return field_value
    
    @validator("reference_table")
    def check_reference(cls, reference_table, values):
        is_controled = values["is_controled"]
        if reference_table is not None and is_controled is False:
            raise ValueError(f"{reference_table} is set. Set is_controled to True")
        else:
            return reference_table

    @validator("admin")
    def check_admin(cls, admin, values):
        field = values["field"]
        admin = values["is_controled"]
        if admin == -1:
             raise ValueError(f"{field} MUST be display in admin")
         
    def build_model_property(self, lang):
        py_type = self.convert()

        if not self.required:
            line = f"{self.field}: Optional"
            if self.is_multiple:
                line += f"[List[{py_type}]]"
            else:
                line += f"[List[{py_type}]]"
        else:
            line = f"{self.field}:{py_type}"
        default = getattr(self, f"default_{lang}")
        if default != "":
            line += f"= {default}"
        return line
        
    def get_display_options_by_lang(self, lang):
        keys = [
            f"name_{lang}",
            f'section_name_display_{lang}',
            f'section_order',
            f'section_name_{lang}',
            f'description_{lang}',
            'admin',
            'list',
            'item'
        ]
        return {k:v for k, v in  self.__dict__.items() if k in keys}

    def build_example_by_lang(self, lang):
        return {self.field: getattr(self, f"example_{lang}")}

    def build_example(self):
        return {"fr": self.example_fr, "en": self.example_en}

    def get_by_lang(self, lang):
        dict_by_lang = {}
        for k, v in self.__dict__.items():
            if k.endswith(lang):
                dict_by_lang[k.split("_")[0]] = v
            else:
                dict_by_lang[k] = v
        setattr(self, f"_{lang}", dict_by_lang)

