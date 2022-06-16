"""
model

"""
# from fileinput import filename
import os
import json
from re import template
from pydantic import constr
from jinja2 import Environment, FileSystemLoader, select_autoescape, exceptions


def load_template(template_name, template_dir="./templates/"):
    '''load Jinja2 template'''
    env = Environment(loader=FileSystemLoader(template_dir),
                      autoescape=select_autoescape())
    return env.get_template(template_name)


class Model(object):
    """Model Generator:
    Generate a model given a set of rules filtered by name of the model

    Args: str(name), list(Object(Rule))

    """

    def __init__(self, name: str, rules: list, lang: constr(regex="^(fr|en)$") = "fr"):
        self.name = name
        self.rules = [r for r in rules if r.model == self.name]
        self.lang = lang
        self.get_references()
        self.get_external_models()
    
    @property
    def is_searchable(self):
        return any([r.search for r in self.rules])
    
    @property
    def has_filter(self):
        return any([r.filter for r in self.rules])
    
    @property
    def is_multilang(self) -> bool:
        """define is model is multilang"""
        return any([r.translation for r in self.rules])

    @property
    def types(self):
        '''defining model types Model ModelFilter ModelMultilang'''
        types = [None]
        if self.is_multilang:
            types.append("multilang")
        if self.has_filter:
            types.append("filter")
        return types
    @property
    def filter_properties(self):
        return {
            r.field: {
                "datatype": r.datatype,
                "external_model": r.external_model_name,
                "reference": r.reference_table,
                "multiple": r.multiple,
            }
            for r in self.rules
            if r.filter
        }
    @property
    def filter_fields(self):
        return list(self.filter_properties.keys())
    
    @property
    def search_fields(self):
        return [r.field for r in self.rules if r.search]
    
    @property
    def index_mapping(self):
        return {
                "fr": {
                    "properties": {
                        r.field: r.get_index_property("fr")
                        for r in self.rules
                        if r.field in self.index_fields
                    }
                },
                "en": {
                    "properties": {
                        r.field: r.get_index_property("en")
                        for r in self.rules
                        if r.field in self.index_fields
                    }
                },
            }
    @property    
    def index_fields(self):
        return list(set(self.search_fields + self.filter_fields))
            
    

    def get_external_models(self, type=None):
        """Given the model type get the external models linked in the model"""
        if type is None:
            self.has_external_models = any(
                [r.external_model_name not in [None, "reference"]
                    for r in self.rules]
            )
            self.external_models = list(
                set(
                    r.external_model_name
                    for r in self.rules
                    if r.external_model_name not in [None, "reference"]
                )
            )
        elif type == "filter":
            self.has_external_models = any(
                [r.external_model_name not in [None, "reference"]
                    for r in self.rules if r.filter]
            )
            self.external_models = list(
                set(
                    r.external_model_name
                    for r in self.rules if r.filter
                    if r.external_model_name not in [None, "reference"]
                )
            )
        elif type == "multilang":
            self.has_external_models = any(
                [r.external_model_name not in [None, "reference"]
                    for r in self.rules if r.translation]
            )
            self.external_models = list(
                set(
                    r.external_model_name
                    for r in self.rules if r.translation
                    if r.external_model_name not in [None, "reference"]
                )
            )
        self.external_model_classes = [n.title() for n in self.external_models]
    
    def get_references(self):
        self.has_references = any(
            [r.reference_table is not None for r in self.rules])
        self.reference_tables = list(
            set(
                [r.reference_table for r in self.rules if r.reference_table is not None]
            )
        )
        self.references = list(
            set(
                [
                    (r.field, r.reference_table)
                    for r in self.rules
                    if r.reference_table is not None
                ]
            )
        )
        

    def get_by_lang(self):
        """get the model for the corresponding lang"""
        if self.is_multilang:
            # self.rules_by_lang = {}
            # setattr(self, f"rules_{self.lang}", {})
            return [r.get_by_lang(self.lang) for r in self.rules]

    def build_model(self, type = None):
        """ generate properties for a pydantic model 
        if type is None:
            where model = "dataset" >>> Dataset(Model)
        else:
            type == filter
            where model = "dataset" >>> DatasetFilter(Model)
            type == doc
            where model = "dataset" >>> DatasetMultiLang(Model)
        """
        if type is None:
            self.model_name = self.name.title()
        else:
            self.model_name = f"{self.name.title()}{type.title()}"
        if type is None:
            self.model_properties = [r.get_model_property(self.lang) for r in self.rules]
        elif type == "filter":
            self.model_properties = [r.get_model_property(self.lang) for r in self.rules if r.filter]
        elif type == "multilang":
            self.model_properties = [r.get_model_property(self.lang) for r in self.rules if r.translation]
        if self.has_external_models:
            self.import_external_models = [f"from apps.{model_name}.models import {model_name_class}" for model_name, model_name_class in zip(
                self.external_models, self.external_model_classes)]
        self.build_example()        

    # def build_multilang_model(self):
    #     if self.is_multilang:
    #         self.build_model("multilang")
            

    # def build_filter_model(self):
    #     if self.has_filter:
    #         self.build_model("filter")

    def build_example(self, type=None):
        self.example = {}
        for r in self.rules:
            if type is None:
                self.example.update(r.build_example_by_lang(self.lang))
            if type == "filter":
                if r.filter:
                    self.example.update(r.build_example_by_lang(self.lang))
            if type == "multilang":
                #build example by lang
                if r.translation:
                    self.example.update(r.build_example_by_lang(self.lang))
        return self.example

    def build_reference_values(self):
        raise NotImplementedError("Using apps.dataset.routers get_references values method")

    def write_model(self):
        """Generate the  FastAPI model python file"""
        for type in self.types:    
            self.build_model(type)
            self.build_example(type)
            self.file = f"{self.model_name}-model.py"
            template = load_template("Model.tpl")
            with open(self.file, "w") as f:
                py_file = template.render(
                    model_name=self.model_name,
                    model_properties=self.model_properties,
                    has_external_models = self.has_external_models,
                    external_models = self.import_external_models,
                    has_references = self.has_references,
                    references = self.references,   
                    example = self.example
                )
                f.write(py_file)
