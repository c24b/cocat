"""
model

"""
import os
from re import template
from pydantic import constr
from jinja2 import Environment, FileSystemLoader, select_autoescape, exceptions

from cocat.vocabulary import Vocabulary


def load_template(template_name, template_dirname="templates"):
    """load Jinja2 template"""
    template_dir = os.path.join(os.path.dirname(__file__), template_dirname)
    env = Environment(
        loader=FileSystemLoader(template_dir), autoescape=select_autoescape()
    )
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
        # self.get_references()
        # self.get_external_models()

    
    @property
    def has_vocabulary(self) -> bool:
        return any([r.is_vocabulary for r in self.rules])
    
    @property
    def vocabularies(self) -> dict:
        if self.has_vocabulary:
            return {
                    r.field: {
                    "vocabulary":r.vocabulary, 
                    "vocabulary_name": r.vocabulary.name, 
                    "names_fr": r.vocabulary.names_fr,
                    "names_en": r.vocabulary.names_en
                    }
                
                    for r in self.rules
                }
        return None
    
    @property
    def has_external_model(self) -> bool:
        return any([r.has_external_model for r in self.rules])
    @property
    def external_models(self) -> dict:
        if self.has_external_model:
            return {
                    r.field: { 
                        "external_model_name": r.external_model_name, 
                        "display_keys": r.external_model_display_keys
                    } 
                
                for r in self.rules
            }
        return None

    @property
    def is_multilang(self) -> bool:
        """define is model is multilang"""
        return any([r.translation for r in self.rules])

    @property
    def multilang(self) -> list:
        """get the model for the corresponding lang"""
        if self.is_multilang:
            return {
                r.field: r.get_by_lang(self.lang)
                
                for r in self.rules
            }
        return None
        
    @property
    def is_searchable(self) -> bool:
        """determine if model has full texte search capabilities"""
        return any([r.search for r in self.rules])

    @property
    def search(self) -> dict:
        """define the properties of SearchModel"""
        return {
            r.field: {
                "datatype": r.datatype,
                "external_model": r.external_model_name,
                "vocabulary": r.vocabulary,
                "multiple": r.multiple,
            }
            for r in self.rules
            if r.search
        }

    @property
    def has_filter(self) -> bool:
        """determine if model has filter capabilities"""
        return any([r.filter for r in self.rules])

    @property
    def filters(self) -> dict:
        """define the properties of a ModelFilter"""
        return {
            r.field: {
                "datatype": r.datatype,
                "external_model": r.external_model_name,
                "vocabulary": r.vocabulary,
                "multiple": r.multiple,
            }
            for r in self.rules
            if r.filter
        }

    @property
    def has_index(self) -> bool:
        """determine if model has index capabilities"""
        return any([self.is_searchable, self.has_filter])
    
    @property
    def index(self) -> dict:
        """define the indexed properties of the Model in order to copy it into index"""
        return {**self.search, **self.filter}

    @property
    def mapping(self) -> dict:
        """define the elastic search mapping"""
        if self.has_index:
            if self.is_multilang:
                return {
                    "fr": {
                        "properties": {
                            r.field: r.get_index_property("fr")
                            for r in self.rules
                            if r.field in self.index_properties.keys()
                        }
                    },
                    "en": {
                        "properties": {
                            r.field: r.get_index_property("en")
                            for r in self.rules
                            if r.field in self.index_properties.keys()
                        }
                    },
                }
            else:
                # default lang is en
                return {
                    "properties": {
                        r.field: r.get_index_property("en")
                        for r in self.rules
                        if r.field in self.index_properties.keys()
                    }
                }
        return None
    

    @property
    def example(self) -> dict:
        example = {}
        for r in self.rules:
            example.update(r.build_example_by_lang(self.lang))
        return example
    
    @property
    def properties(self) -> list:
        return  [
                r.get_model_property(self.lang) for r in self.rules
        ]
    # @property
    # def types(self) -> list:
    #     """defining if model has additionnal model types such as: ModelFilter ModelMultilang"""
    #     types = [None]
    #     if self.is_multilang:
    #         types.append("multilang")
    #     if self.has_filter:
    #         types.append("filter")
    #     return types
            
    def build_model(self, type=None):
        """generate properties for a pydantic model
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
        self.get_properties(type)
        self.get_external_models(type)
        self.import_external_models = [
            f"from apps.models.{model_name} import {model_name_class}"
            for model_name, model_name_class in zip(
                self.external_models, self.external_model_classes
            )
        ]
        self.build_example()

    def build_router(self, type=None):
        """Build router capabilities"""
        if self.has_external_models:
            self.import_external_models = [
                f"from apps.models.{model_name} import {model_name_class}"
                for model_name, model_name_class in zip(
                    self.external_models, self.external_model_classes
                )
            ]
        self.import_models = [
            f"from apps.models.{self.name} import {self.name.title()}"
        ]
        self.models = [self.name.title()]
        for type in self.types:
            if type is not None:
                model_name = f"{self.name.title()}{type.title()}"
                self.import_models.append(
                    f"from apps.models.{self.name} import {model_name}"
                )
                self.models.append(model_name)
        # self.has_references
        # self.references

    def build_example(self, type=None) -> dict:

        if type is None:
            rules = self.rules
        elif type == "filter":
            rules = [r for r in self.rules if r.filter]
        elif type == "multilang":
            rules = [r for r in self.rules if r.translation]
        self.example = {}
        for r in rules:
            self.example.update(r.build_example_by_lang(self.lang))
        return self.example

    def build_reference_values(self):
        # for rule in self.rules:
        #     if rule.reference()
        raise NotImplementedError(
            "Using apps.dataset.routers get_references values method"
        )

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
                    has_external_models=self.has_external_models,
                    external_models=self.import_external_models,
                    has_references=self.has_references,
                    references=self.references,
                    example=self.example,
                )
                f.write(py_file)

    def write_router(self):
        with open(self.file, "w") as f:
            py_file = template.render(
                models=[],
                import_model=self.import_external_models,
                search=self.is_search_model,
                filter=self.is_filter_model,
            )
            f.write(py_file)
