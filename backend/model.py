"""
model

"""
from pydantic import constr

class Model(object):
    """Model Generator:
    Generate a model given a set of rules filtered by name of the model

    Args: str(name), list(Object(Rule))

    """

    def __init__(self, name:str, rules:list, lang: constr(regex="^(fr|en)$")= "fr")):
        self.name = name
        self.rules = [r for r in rules if r.model == self.name]
        self.lang = lang
        self.get_filter_properties()

    def get_filter_properties(self):
        """get_filter_properties define if the model has filter and the type of each filter"""
        self.reference_tables = [r.reference_table for r in self.rules if r.reference_table is not None]
        self.filters = {
            r.field: {
                "datatype": r.datatype,
                "external_model": r.external_model_name,
                "reference": r.reference_table
            }
            for r in self.rules
            if r.filter
        }
        self.has_filter = any([r.filter for r in self.rules])
        self.filter_fields = [r.field for r in self.rules  if r.filter]
        return self.filters
    
    def get_search_properties(self):
        """define if model is searchable"""
        self.is_searchable = any([r.search for r in self.rules])
        if self.is_searchable:
            self.search_fields = [r.field for r in self.rules  if r.search]
        return self
    def is_multilang(self):
        """define is model is multilang"""
        self.is_multilang = any(
        [
            r.translation
            for r in self.rules
        ]
        )
    def to_be_indexed(self):
        """define is model has to be indexed"""
        self.to_index = False
        self.indexed_fields
        if self.is_searchable or self.has_filters:
            self.to_index = True
            self.indexed_fields = list(set(self.search_fields + self.indexed_fields))
        
    def get_external_models(self):
        self.external_models = list(set(r.external_model_name for r in self.rules))
        self.external_model_classes = [n.title() for n in self.external_models]

    def get_by_lang(self):
        self.rules_by_lang = {}
        # setattr(self, f"rules_{self.lang}", {})
        for r in self.rules:
            self.rules_by_lang[r.field] = r.get_by_lang(self.lang)        
        
    def build_model(self):
        """"generate properties for a pydantic model where model = "dataset" >>> Dataset(Model)"""
        self.model_properties = []
        for r in self.rules:
            if self.is_multilang:
                self.model_properties.append(r.build_model_property(self.lang))

        pass
    def build_doc_model(self):
        pass
    def build_filter_model(self):
        pass
    def map_model_with_values(self):
        pass
    def build_example(self):
        pass
    
    def build_reference_values(self):
        pass