"""
model

"""
import json
from pydantic import constr


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
        self.filters =  {
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
                    "properties":{r.field: r.get_index_property("fr") for r in self.rules if r.field in self.index_fields}
                    
                },
                "en": {
                    "properties":{r.field: r.get_index_property("en") for r in self.rules if r.field in self.index_fields}
                }
            }

    def is_multilang(self) -> bool:
        """define is model is multilang"""
        self.is_multilang = any([r.translation for r in self.rules])

    def get_external_models(self):
        """get [("field","external_model")"""
        self.has_external_models = any([r.external_model_name not in [None, "reference"] for r in self.rules])
        self.external_models = list(
            set(
                r.external_model_name
                for r in self.rules
                if r.external_model_name is not None
            )
        )
        self.external_model_classes = [n.title() for n in self.external_models]

    def get_references(self):
        self.has_references = any([r.reference_table is not None for r in self.rules])
        self.reference_tables = list(set([r.reference_table
                    for r in self.rules
                    if r.reference_table is not None]))
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
            
    
    def build_model(self):
        """ "generate properties for a pydantic model where model = "dataset" >>> Dataset(Model)"""
        self.model_name = f"class {self.name.title()}(BaseModel)"
        self.model_properties = []
        for r in self.rules:
            self.model_properties.append(r.get_model_property(self.lang))

    def build_doc_model(self):
        if self.is_multilang:
            pass

    def build_filter_model(self):
        if self.has_filter:
            pass

    
    def build_example(self):
        pass

    def build_reference_values(self):
        if self.has_references:
            pass
