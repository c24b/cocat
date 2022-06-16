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
        self.has_filter = None
        self.is_searchable = None
        self.to_index = None
        self.has_references = None
        self.has_external_models = None
        self.is_multilang()
        self.get_filter_properties()
        self.get_search_properties()
        self.get_index_properties()
        self.get_references()
        self.get_external_models()

    def get_filter_properties(self):
        """set filters and has_filter with  type of each filter"""
        self.filters = {
            r.field: {
                "datatype": r.datatype,
                "external_model": r.external_model_name,
                "reference": r.reference_table,
                "multiple": r.multiple,
            }
            for r in self.rules
            if r.filter
        }
        self.filter_fields = list(self.filters.keys())
        self.has_filter = any([r.filter for r in self.rules])
        return self

    def get_search_properties(self):
        """define if model is searchable"""
        self.is_searchable = any([r.search for r in self.rules])
        if self.is_searchable:
            self.search_fields = [r.field for r in self.rules if r.search]
        return self

    def get_index_properties(self):
        """get all the properties of the model that have to be indexed
        prepare mapping
        """
        self.to_index = False
        if self.is_searchable is None:
            self.get_search_properties()
        if self.has_filter is None:
            self.get_filter_properties()
        if self.is_searchable or self.has_filter:
            self.to_index = True
            self.index_fields = self.search_fields + self.filter_fields
            self.index_mapping = {
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

    def is_multilang(self) -> bool:
        """define is model is multilang"""
        self.is_multilang = any([r.translation for r in self.rules])

    def get_external_models(self):
        """get [("field","external_model")"""
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

    def build_model(self, model_type = None):
        """ generate properties for a pydantic model 
        if model_type is None:
            where model = "dataset" >>> Dataset(Model)
        else:
            model_type == filter
            where model = "dataset" >>> DatasetFilter(Model)
            model_type == doc
            where model = "dataset" >>> DatasetDoc(Model)
        """
        if model_type is None:
            model_name = self.name.title()
        else:
            model_name = f"{self.name.title()}{model_type.title()}"
        self.model_name = f"class {model_name}(BaseModel)"
        self.model_properties = [r.get_model_property(self.lang) for r in self.rules]
        if self.has_external_models:
            self.import_external_models = [f"from apps.{model_name}.models import {model_name_class}" for model_name, model_name_class in zip(
                self.external_models, self.external_model_classes)]
        self.build_example()        

    def build_doc_model(self):
        if self.is_multilang:
            pass

    def build_filter_model(self):
        if self.has_filter:
            pass

    def build_example(self):
        self.example = {}
        for r in self.rules:
            self.example.update(r.build_example_by_lang(self.lang))
        return self.example

    def build_reference_values(self):
        if self.has_references:
            pass

    def write_model(self):
        """Generate the  FastAPI model python file"""
        self.build_model()
        self.build_example()
        self.file = f"{self.name}-model.py"
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
