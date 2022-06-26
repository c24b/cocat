import os
from csv import DictReader
import datetime
import json
import itertools
from pydantic import ValidationError
import pytest
from cocat.vocabulary import Vocabulary
from cocat.property import Property, CSVPropertyImporter

def test_property_is_reference():
    property_d = {' issue_date': '2022-05-22',
    'admin_display_order': '18',
    'comment': 'champ par défault en cours de construction',
    'constraint': 'one of',
    'datatype': 'string',
    'default_en': 'N/D',
    'default_fr': 'N/D',
    'description_en': "''",
    'description_fr': '"Ce champ permet de définir le milieu concerné par la '
                    'ressource à partir d\'un vocabulaire contrôlé interne"',
    'example_en': 'N/D',
    'example_fr': 'N/D',
    'external_model_display_keys': 'name|id',
    'external_model_name': 'reference',
    'field': 'environment_detail',
    'filter': 'False',
    'format': '',
    'inspire': '',
    'item_display_order': '18',
    'list_display_order': '18',
    'model': 'dataset',
    'multiple': 'True',
    'name_en': 'Environment',
    'name_fr': 'Milieu',
    'reference_table': 'ref_environment_detail',
    'required': 'True',
    'search': 'True',
    'translation': 'True',
    'vocab': 'dcat:themeTaxonomy: skos'
        }
    r = Property.parse_obj(property_d)
    assert r.is_reference is True, r.is_reference
    
def test_empty_vocabulary_in_property():
    property_d = {' issue_date': '2022-05-22',
    'admin_display_order': '18',
    'comment': 'champ par défault en cours de construction',
    'constraint': 'one of',
    'datatype': 'string',
    'default_en': 'N/D',
    'default_fr': 'N/D',
    'description_en': "''",
    'description_fr': '"Ce champ permet de définir le milieu concerné par la '
                    'ressource à partir d\'un vocabulaire contrôlé interne"',
    'example_en': 'N/D',
    'example_fr': 'N/D',
    'external_model_display_keys': 'name|id',
    'external_model_name': 'reference',
    'field': 'environment_detail',
    'filter': 'False',
    'format': '',
    'inspire': '',
    'item_display_order': '18',
    'list_display_order': '18',
    'model': 'dataset',
    'multiple': 'True',
    'name_en': 'Environment',
    'name_fr': 'Milieu',
    'reference_table': 'ref_environment_detail',
    'required': 'True',
    'search': 'True',
    'translation': 'True',
    'vocab': 'dcat:themeTaxonomy: skos'
    }
    r = Property.parse_obj(property_d)
    assert r.is_reference is True, r.is_reference
    assert r.reference == Vocabulary(name="ref_environment_detail", lang="fr")
    assert r.reference.labels == []

def test_init_vocabulary_in_property():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr", csv_file = fname)
    property_d = {' issue_date': '2022-05-22',
    'admin_display_order': '18',
    'comment': 'champ par défault en cours de construction',
    'constraint': 'one of',
    'datatype': 'string',
    'default_en': 'N/D',
    'default_fr': 'N/D',
    'description_en': "''",
    'description_fr': '"Ce champ permet de définir le milieu concerné par la '
                    'ressource à partir d\'un vocabulaire contrôlé interne"',
    'example_en': 'N/D',
    'example_fr': 'N/D',
    'external_model_display_keys': 'name|id',
    'external_model_name': 'reference',
    'field': 'environment_detail',
    'filter': 'False',
    'format': '',
    'inspire': '',
    'item_display_order': '18',
    'list_display_order': '18',
    'model': 'dataset',
    'multiple': 'True',
    'name_en': 'Environment',
    'name_fr': 'Milieu',
    'reference_table': 'environment',
    'required': 'True',
    'search': 'True',
    'translation': 'True',
    'vocab': 'dcat:themeTaxonomy: skos'
    }
    r = Property.parse_obj(property_d)
    assert r.is_reference is True, r.is_reference
    assert r.reference == Vocabulary(name="environment", lang="fr")
    assert r.reference.names_fr == ["Air", "Eau","Sols", "Alimentation"], r.reference.names_fr
    assert r.reference.labels == ["Air", "Eau","Sols", "Alimentation"], r.reference.labels
    v.delete()
    
def test_property_001():
    """
    test init from a fake oneliner csv
    """
    header = "field,model,name_fr,name_en,external_model_name,external_model_display_keys,reference_table,vocab,inspire,translation,multiple,constraint,datatype,format,search,filter,admin_display_order,list_display_order,item_display_order,required,description_fr,description_en,example_fr,example_en,default_fr,comment,default_en, issue_date"
    value = """environment_detail,dataset,Milieu,Environment,reference,name|id,ref_environment_detail,dcat:themeTaxonomy: skos,,True,True,one of,string,,True,False,18,18,18,True,"Ce champ permet de définir le milieu concerné par la ressource à partir d'un vocabulaire contrôlé interne",'',N/D,N/D,N/D,champ par défault en cours de construction,N/D,2022-05-22"""
    property_d = dict(zip(header.split(","), value.split(",")))
    assert property_d["external_model_name"] == "reference"
    assert property_d["external_model_display_keys"] == "name|id"
    r = Property.parse_obj(property_d)
    assert r.multiple
    assert r.required
    assert r.filter is False, r.filter
    assert r.search is True, r.search
    assert r.external_model_name == "reference"
    assert r.external_model_display_keys == ["name", "id"]
    assert r.admin_display_order != -1
    assert r.external_model_name == "reference" and r.reference_table != ""
    assert r.issue_date == datetime.date.today()


def test_property_validation_002():
    property_d = {
        "field": "title",
        "model": "dataset",
        "datatype": "string",
        "format": "",
        "constraint": "unique",
        "reference_table": "",
        "external_model_name": "",
        "external_model_display_keys": "",
        "required": "True",
        "is_controled": "False",
        "multiple": "False",
        "translation": "True",
        "search": "True",
        "filter": "False",
        "name_fr": "Titre du jeu de données",
        "name_en": "",
        "description_fr": "Ce champ spécifie le nom de la ressource,son titre,",
        "description_en": "",
        "default_fr": "",
        "default_en": "",
        "example_fr": "Base de données des adresses nationales",
        "example_en": "",
        "admin_display_order": "1",
        "list_display_order": "1",
        "item_display_order": "1",
        "vocab": "dcat:title",
        "inspire": "",
        "comment": "",
    }
    assert property_d["external_model_name"] == ""
    r = Property.parse_obj(property_d)
    assert r.name_fr == "Titre du jeu de données"
    assert r.datatype == "string"
    assert r.filter is False
    assert r.search is True
    assert r.reference_table is None
    assert r.filter is False
    assert r.format is None
    assert r.translation is True
    assert r.admin_display_order == 1
    assert r.external_model_name is None
    assert r.external_model_display_keys is None


def test_property_reference_003():
    property_d = {
        "field": "tags",
        "model": "dataset",
        "datatype": "string",
        "format": "",
        "constraint": "unique",
        "reference_table": "ref_tags",
        "external_model_name": "reference",
        "external_model_display_keys": "name",
        "required": "True",
        "is_controled": "True",
        "multiple": "True",
        "translation": "True",
        "search": "True",
        "filter": "False",
        "name_fr": "Mots clés",
        "name_en": "",
        "description_fr": "",
        "description_en": "",
        "default_fr": "",
        "default_en": "",
        "example_fr": "chlordécone|cancer",
        "example_en": "",
        "admin_display_order": "2",
        "list_display_order": "2",
        "item_display_order": "2",
        "vocab": "dcat:themeTaxonomy",
        "inspire": "",
        "comment": "",
    }
    assert property_d["reference_table"] == "ref_tags"
    assert property_d["external_model_name"] == "reference"
    r = Property.parse_obj(property_d)
    assert r.reference_table is not None
    assert r.reference_table == "ref_tags"
    assert r.external_model_name == "reference"
    assert r.external_model_display_keys == ["name"]
    assert r.get_field_by_lang("fr") == "tags", r.get_field_by_lang("fr")


# def test_property_validation_error_004():
#     property_d_0 = {
#         "field": "title",
#         "model": "dataset",
#         "datatype": "integer",
#         "format": "",
#         "constraint": "unique",
#         "reference_table": "",
#         "external_model": "",
#         "external_model_display_keys": "",
#         "required": "True",
#         "is_controled": "False",
#         "multiple": "False",
#         "translation": "True",
#         "search": "True",
#         "filter": "False",
#         "name_fr": "Titre du jeu de données",
#         "name_en": "",
#         "description_fr": "Ce champ spécifie le nom de la ressource,son titre,",
#         "description_en": "",
#         "default_fr": "",
#         "default_en": "",
#         "example_fr": "Base de données des adresses nationales",
#         "example_en": "",
#         "admin_display_order": "1",
#         "list_display_order": "1",
#         "item_display_order": "1",
#         "vocab": "dcat:title",
#         "inspire": "",
#         "comment": "",
#     }

#     with pytest.raises(ValidationError) as excinfo:
#         r = Property.parse_obj(property_d_0)
#     error = str(excinfo.value).split("\n")
#     assert error == ['1 validation error for Property', 'search', "  title search option is set to True, it can't be index in full text: invalid integer. Set search option to False (type=value_error)"], error
#     # assert (error[0]) == "", error[0]

# def test_validation_error_005():
# property_d_1 = {
#     "field": "tags",
#     "model": "dataset",
#     "datatype": "string",
#     "format": "",
#     "constraint": "unique",
#     "reference_table": "ref_tags",
#     "external_model": "",
#     "external_model_display_keys": "name",
#     "required": "True",
#     "is_controled": "False",
#     "multiple": "True",
#     "translation": "True",
#     "search": "True",
#     "filter": "False",
#     "name_fr": "Mots clés",
#     "name_en": "",
#     "description_fr": "",
#     "description_en": "",
#     "default_fr": "",
#     "default_en": "",
#     "example_fr": "chlordécone|cancer",
#     "example_en": "",
#     "admin_display_order": "2",
#     "list_display_order": "2",
#     "item_display_order": "2",
#     "vocab": "dcat:themeTaxonomy",
#     "inspire": "",
#     "comment": "",
# }

# with pytest.raises(ValidationError) as excinfo:
#     r = Property.parse_obj(property_d_1)

# assert str(excinfo.value.split("\n")) == ["boo!"],excinfo.value.split("\n")


def test_csv_import_005():
    """test with csv file"""
    propertys = []
    with open(os.path.join(os.path.dirname(__file__),"test_propertys.csv"), "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            property_d = dict(row.items())
            # for k, v in row.items():
            #     property_d[k] = cast_type_from_str_to_python(v)
            r = Property.parse_obj(property_d)
            propertys.append(r)
    assert len(propertys) == 1, propertys

def test_csv_import_008():
    fname = os.path.join(os.path.dirname(__file__), 'propertys.csv')
    assert "backend/tests" in fname, fname
    c = CSVPropertyImporter(fname)
    assert len(c.propertys) == 52
