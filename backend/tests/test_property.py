import os
from csv import DictReader
import datetime
import json
import itertools
from pydantic import ValidationError
import pytest
from cocat.vocabulary import Vocabulary
from cocat.property import Property, CSVPropertyImporter

    
def test_property_init_001():
    """
    test init from a fake oneliner csv
    """
    header = "field,model,name_fr,name_en,external_model_name,external_model_display_keys,datatype,vocabulary_name,vocabulary_label,vocabulary_filename,inspire,translation,multiple,constraint,datatype,format,search,filter,admin_display_order,list_display_order,item_display_order,required,description_fr,description_en,example_fr,example_en,default_fr,comment,default_en, issue_date"
    value = """environment_detail,dataset,Milieu,Environment,vocabulary,name|id,string,environment, environment, ref_environment_detail.csv,dcat:themeTaxonomy: skos,,True,True,one of,string,,True,False,18,18,18,True,"Ce champ permet de définir le milieu concerné par la ressource à partir d'un vocabulary_labelulaire contrôlé interne",'',N/D,N/D,N/D,champ par défault en cours de construction,N/D,2022-05-22"""
    property_d = dict(zip(header.split(","), value.split(",")))
    assert property_d["external_model_name"] == "vocabulary"
    assert property_d["external_model_display_keys"] == "name|id"
    assert property_d["vocabulary_name"] == "environment"
    r = Property.parse_obj(property_d)
    assert r.multiple
    assert r.required
    assert r.filter is False, r.filter
    assert r.search is True, r.search
    assert r.external_model_name == "vocabulary", r.external_model_name
    assert r.external_model_display_keys == ["name", "id"]
    assert r.admin_display_order != -1
    assert r.vocabulary.name == "environment_detail", r.vocabulary_name
    assert r.issue_date == datetime.date.today()


def test_property_validation_002():
    property_d = {
        "field": "title",
        "model": "dataset",
        "datatype": "string",
        "format": "",
        "constraint": "unique",
        "vocabulary_name": "",
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
        "vocabulary_label": "dcat:title",
        "inspire": "",
        "comment": "",
    }
    assert property_d["external_model_name"] == ""
    r = Property.parse_obj(property_d)
    assert r.name_fr == "Titre du jeu de données"
    assert r.datatype == "string"
    assert r.filter is False
    assert r.search is True
    assert r.vocabulary is None
    assert r.filter is False
    assert r.format is None
    assert r.translation is True
    assert r.admin_display_order == 1
    assert r.external_model_name is None
    assert r.external_model_display_keys is None


def test_property_vocabulary_003():
    property_d = {
        "field": "tags",
        "model": "dataset",
        "datatype": "string",
        "format": "",
        "constraint": "unique",
        "vocabulary_name": "ref_tags",
        "external_model_name": "vocabulary",
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
        "vocabulary_label": "dcat:themeTaxonomy",
        "inspire": "",
        "comment": "",
    }
    assert property_d["vocabulary_name"] == "ref_tags"
    assert property_d["external_model_name"] == "vocabulary"
    r = Property.parse_obj(property_d)
    assert r.is_vocabulary == True
    assert r.external_model_name == "vocabulary"
    assert r.external_model_display_keys == ["name"]
    assert r.get_field_by_lang("fr") == "tags", r.get_field_by_lang("fr")


def test_property_validation_error_004():
    property_d_0 = {
        "field": "title",
        "model": "dataset",
        "datatype": "integer",
        "format": "",
        "constraint": "unique",
        "vocabulary_name": "",
        "external_model": "",
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
        "vocabulary_label": "dcat:title",
        "inspire": "",
        "comment": "",
    }

    with pytest.raises(ValidationError) as excinfo:
        r = Property.parse_obj(property_d_0)
    error = str(excinfo.value).split("\n")
    assert error == ['1 validation error for Property', 'search', "  title search option is set to True, it can't be index in full text: invalid integer. Set search option to False (type=value_error)"], error
    # assert (error[0]) == "", error[0]

def test_validation_error_005():
    property_d_1 = {"field": "tags",
    "model": "dataset",
    "datatype": "string",
    "format": "",
    "constraint": "unique",
    "vocabulary_name": "ref_tags",
    "external_model": "",
    "external_model_display_keys": "name",
    "required": "True",
    "is_controled": "False",
    "multiple": "True",
    "translation": "True",
    "search": "True",
    "filter": "False",
    "name_fr": "Mots clés",
    
    "field": "tags",
    "model": "dataset",
    "datatype": "string",
    "format": "",
    "constraint": "unique",
    "vocabulary_name": "ref_tags",
    "external_model": "",
    "external_model_display_keys": "name",
    "required": "True",
    "is_controled": "False",
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
    "vocabulary_label": "dcat:themeTaxonomy",
    "inspire": "",
    "comment": "",
    }

    with pytest.raises(ValidationError) as excinfo:
        r = Property.parse_obj(property_d_1)
    error = str(excinfo.value).split("\n")
    assert error == [
        '1 validation error for Property', 
        'external_model_display_keys', 
        "  As external_model keys are declared, external model should be specified "
        "(type=value_error)"
        ], error

def test_csv_import_005():
    """test with csv file"""
    properties = []
    with open(os.path.join(os.path.dirname(__file__),"test_rules.csv"), "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            property_d = dict(row.items())
            # for k, v in row.items():
            #     property_d[k] = cast_type_from_str_to_python(v)
            r = Property.parse_obj(property_d)
            properties.append(r)
    assert len(properties) == 1, properties

def test_csv_import_006():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    assert "backend/tests" in fname, fname
    c = CSVPropertyImporter(fname)
    assert len(c.properties) == 52


def test_property_is_vocabulary_007():
    property_d = {' issue_date': '2022-05-22',
    'admin_display_order': '18',
    'comment': 'champ par défault en cours de construction',
    'constraint': 'one of',
    'datatype': 'string',
    'default_en': 'N/D',
    'default_fr': 'N/D',
    'description_en': "''",
    'description_fr': '"Ce champ permet de définir le milieu concerné par la '
                    'ressource à partir d\'un vocabulary_labelulaire contrôlé interne"',
    'example_en': 'N/D',
    'example_fr': 'N/D',
    'external_model_display_keys': 'name|id',
    'external_model_name': 'vocabulary',
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
    'vocabulary_name': 'ref_environment_detail',
    'required': 'True',
    'search': 'True',
    'translation': 'True',
    'vocabulary_label': 'dcat:themeTaxonomy: skos'
        }
    r = Property.parse_obj(property_d)
    assert r.is_vocabulary is True, r.is_vocabulary
    
def test_empty_vocabulary_in_property_008():
    property_d = {' issue_date': '2022-05-22',
    'admin_display_order': '18',
    'comment': 'champ par défault en cours de construction',
    'constraint': 'one of',
    'datatype': 'string',
    'default_en': 'N/D',
    'default_fr': 'N/D',
    'description_en': "''",
    'description_fr': '"Ce champ permet de définir le milieu concerné par la '
                    'ressource à partir d\'un vocabulary_labelulaire contrôlé interne"',
    'example_en': 'N/D',
    'example_fr': 'N/D',
    'external_model_display_keys': 'name|id',
    'external_model_name': 'vocabulary',
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
    'vocabulary_name': 'ref_environment_detail',
    'required': 'True',
    'search': 'True',
    'translation': 'True',
    'vocabulary_label': 'dcat:themeTaxonomy: skos'
    }
    r = Property.parse_obj(property_d)
    assert r.is_vocabulary is True, r.is_vocabulary
    assert isinstance(r.vocabulary, Vocabulary)
    assert r.vocabulary.labels == []

def test_init_vocabulary_in_property_009():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr", csv_file = fname)
    assert v.name == "environment", v.name
    property_d = {' issue_date': '2022-05-22',
    'admin_display_order': '18',
    'comment': 'champ par défault en cours de construction',
    'constraint': 'one of',
    'datatype': 'string',
    'default_en': 'N/D',
    'default_fr': 'N/D',
    'description_en': "''",
    'description_fr': '"Ce champ permet de définir le milieu concerné par la '
                    'ressource à partir d\'un vocabulary_labelulaire contrôlé interne"',
    'example_en': 'N/D',
    'example_fr': 'N/D',
    'external_model_display_keys': 'name|id',
    'external_model_name': 'vocabulary',
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
    'vocabulary_name': 'environment',
    'vocabulary_filename': 'vocabularies/environment.csv',
    'required': 'True',
    'search': 'True',
    'translation': 'True',
    'vocabulary_label': 'dcat:themeTaxonomy: skos'
    }
    r = Property.parse_obj(property_d)
    assert r.is_vocabulary is True, r.is_vocabulary
    assert r.vocabulary.csv_file is not None
    assert r.vocabulary.names_fr == ["Air", "Eau","Sols", "Alimentation"], r.vocabulary.names_fr
    assert r.vocabulary.labels == ["Air", "Eau","Sols", "Alimentation"], r.vocabulary.labels
    v.delete()

def test_vocabulary_property_010():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    assert "test_rules" in fname, fname
    c = CSVPropertyImporter(fname)
    assert len(c.properties) == 52
    for prop in c.properties:
        if prop.is_vocabulary:
            assert prop.vocabulary.labels is not None, prop.vocabulary.labels