"""
model

"""
from lib2to3.refactor import RefactoringTool
import os
from re import template
from pydantic import constr


from cocat.vocabulary import Vocabulary
from cocat.property import Property
from cocat.utils import load_template


class Model(object):
    """Model Generator:
    Generate a model given a set of rules filtered by name of the model

    Args: str(name), list(Object(Rule))

    """

    def __init__(self, name: str, rules: list, lang: constr(regex="^(fr|en)$") = "fr"):
        self.name = name
        self.rules = rules
        # self.properties = rules
        self.lang = lang
       
    @property
    def properties(self):
        return [Property.parse_obj(rule) for rule in self.rules]
    
    @property
    def has_vocabulary(self) -> bool:
        return any([r.is_vocabulary for r in self.properties])
    
    @property
    def vocabularies(self) -> dict:
        # if self.has_vocabulary:
            # for r in self.properties: 
            #     if r.is_vocabulary:
            #         r.vocabulary.create()

        return {
                r.field: {
                "labels": r.vocabulary.labels,
                "names_fr": r.vocabulary.names_fr,
                "names_en": r.vocabulary.names_en,
                "uris": r.vocabulary.uris
                }
            
                for r in self.properties if r.is_vocabulary
            }
        
        return {}
    
    @property
    def has_external_model(self) -> bool:
        return any([r.is_external_model for r in self.properties])
    
    @property
    def external_models(self) -> dict:
        if self.has_external_model:
            return {
                    r.external_model_name : {
                        "field": r.field, 
                        "external_model_name": r.external_model_name, 
                        "display_keys": r.external_model_display_keys
                    } 
                
                for r in self.properties if r.is_external_model
            }
        return {}

    @property
    def is_multilang(self) -> bool:
        """define is model is multilang"""
        return any([r.translation for r in self.properties])

    @property
    def multilang(self) -> list:
        """get the model for the corresponding lang"""
        if self.is_multilang:
            return {
                r.field: r
                
                for r in self.properties 
                if r.translation
            }
        return {}
        
    @property
    def is_searchable(self) -> bool:
        """determine if model has full texte search capabilities"""
        return any([r.search for r in self.properties])

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
            for r in self.properties
            if r.search
        }

    @property
    def has_filter(self) -> bool:
        """determine if model has filter capabilities"""
        return any([r.filter for r in self.properties])

    @property
    def filters(self) -> dict:
        """define the properties of a ModelFilter"""
        return {
                r.field: {
                    "datatype": r.datatype,
                    "is_external_model": r.is_external_model,
                    "external_model": r.external_model_name,
                    "external_model_display_keys": r.external_model_display_keys,
                    "is_vocabulary": r.is_vocabulary,
                    "vocabulary": r.vocabulary_name,
                    "is_multiple": r.multiple,
            }
            for r in self.properties
            if r.filter
        }

    @property
    def has_index(self) -> bool:
        """determine if model has index capabilities"""
        return any([self.is_searchable, self.has_filter])
    
    @property
    def index(self) -> dict:
        """define the indexed properties of the Model in order to copy it into index"""
        return {**self.search, **self.filters}

    @property
    def mapping(self) -> dict:
        """define the elastic search mapping"""
        if self.has_index:
            if self.is_multilang:
                return {
                    "fr": {
                        "properties": {
                            r.field: r.get_index_property("fr")
                            for r in self.properties
                            if r.field in self.index.keys()
                        }
                    },
                    "en": {
                        "properties": {
                            r.field: r.get_index_property("en")
                            for r in self.properties
                            if r.field in self.index.keys()
                        }
                    },
                }
            else:
                # default lang is en
                return {
                    "properties": {
                        r.field: r.get_index_property("en")
                        for r in self.properties
                        if r.field in self.index_properties.keys()
                    }
                }
        return None
    

    @property
    def example(self) -> dict:
        example = {}
        for r in self.properties:
            example.update(r.build_example_by_lang(self.lang))
        return example
    @property
    def model_name(self):
        return self.name.title()
    @property
    def pydantic_model(self) -> list:
        return  [
                r.get_pydantic_property(self.lang) for r in self.properties
        ]
    
    @property    
    def import_external_models(self, type=None):
        """generate properties for a pydantic model
        if type is None:
            where model = "dataset" >>> Dataset(Model)
        else:
            type == filter
            where model = "dataset" >>> DatasetFilter(Model)
            type == doc
            where model = "dataset" >>> DatasetMultiLang(Model)
        """
        return [
            f"from apps.models.{model_name} import {model_name.title()}"
            for model_name in self.external_models
        ]
    
    @property
    def import_models(self):
        return f"from apps.models.{self.name} import {self.model_name}"
    
    def build_router(self, type=None):
        """Build router capabilities"""
        # if self.has_external_models:
        #     self.import_external_models = [
        #         f"from apps.models.{model_name} import {model_name_class}"
        #         for model_name, model_name_class in zip(
        #             self.external_models, self.external_model_classes
        #         )
        #     ]
        # self.import_models = [
        #     f"from apps.models.{self.name} import {self.name.title()}"
        # ]
        # self.models = [self.name.title()]
        # for type in self.types:
        #     if type is not None:
        #         model_name = f"{self.name.title()}{type.title()}"
        #         self.import_models.append(
        #             f"from apps.models.{self.name} import {model_name}"
        #         )
        #         self.models.append(model_name)
        raise NotImplementedError    
    
    def build_reference_values(self):
        raise NotImplementedError(
            "Using apps.dataset.routers get_references values method"
        )

    def write_model(self):
        """Generate the  FastAPI model python file"""
        file = f"test-{self.model_name}-model.py"
        template = load_template("Model.tpl")
        with open(file, "w") as f:
            py_file = template.render(
                model_name=self.model_name,
                model_properties=self.pydantic_model,
                has_external_models=self.has_external_model,
                external_models=self.import_external_models,
                has_vocabulary=self.has_vocabulary,
                references=[v["labels"] for k,v in self.vocabularies.items()],
                example=self.example,
            )
            f.write(py_file)

    def write_router(self):
        file = f"test-{self.model_name}-router.py"
        template = load_template("router.tpl")
        with open(file, "w") as f:
            py_file = template.render(
                name = self.name,
                model_name = self.model_name,
                # models=self.pydantic_model,
                import_model=self.import_external_models,
                search=self.is_searchable,
                filter=self.has_filter,
            )
            f.write(py_file)

class FilterModel(Model):
    def __init__(self, name: str, rules: list, lang: constr(regex="^(fr|en)$") = "fr"):
        super().__init__(name, rules, lang)
        self.rules = [r for r in rules if r.filter]
    
    @property
    def model_name(self):
        return self.name.title()+"Filter"
class MultiLangModel(Model):
    def __init__(self, name: str, rules: list, lang: constr(regex="^(fr|en)$") = "fr"):
        super().__init__(name, rules, lang)
        self.rules = [r for r in rules if r.translation]
    @property
    def model_name(self):
        return self.name.title()+"MultiLang"