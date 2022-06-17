import os
from csv import DictReader
import datetime
import json
import itertools
from pydantic import ValidationError
import pytest
from cocat.rule import Rule, CSVRuleImporter


def test_rule_001():
    """
    test init from a fake oneliner csv
    """
    header = "field,model,name_fr,name_en,external_model_name,external_model_display_keys,reference_table,vocab,inspire,translation,multiple,constraint,datatype,format,search,filter,admin_display_order,list_display_order,item_display_order,required,description_fr,description_en,example_fr,example_en,default_fr,comment,default_en, issue_date"
    value = """environment_detail,dataset,Milieu,Environment,reference,name|id,ref_environment_detail,dcat:themeTaxonomy: skos,,True,True,one of,string,,True,False,18,18,18,True,"Ce champ permet de définir le milieu concerné par la ressource à partir d'un vocabulaire contrôlé interne",'',N/D,N/D,N/D,champ par défault en cours de construction,N/D,2022-05-22"""
    rule_d = dict(zip(header.split(","), value.split(",")))
    assert rule_d["external_model_name"] == "reference"
    assert rule_d["external_model_display_keys"] == "name|id"
    r = Rule.parse_obj(rule_d)
    assert r.multiple
    assert r.required
    assert r.filter is False, r.filter
    assert r.search is True, r.search
    assert r.external_model_name == "reference"
    assert r.external_model_display_keys == ["name", "id"]
    assert r.admin_display_order != -1
    assert r.external_model_name == "reference" and r.reference_table != ""
    assert r.issue_date == datetime.date.today()


def test_rule_validation_002():
    rule_d = {
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
    assert rule_d["external_model_name"] == ""
    r = Rule.parse_obj(rule_d)
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


def test_rule_reference_003():
    rule_d = {
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
    assert rule_d["reference_table"] == "ref_tags"
    assert rule_d["external_model_name"] == "reference"
    r = Rule.parse_obj(rule_d)
    assert r.reference_table is not None
    assert r.reference_table == "ref_tags"
    assert r.external_model_name == "reference"
    assert r.external_model_display_keys == ["name"]
    assert r.get_field_by_lang("fr") == "tags", r.get_field_by_lang("fr")


# def test_rule_validation_error_004():
#     rule_d_0 = {
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
#         r = Rule.parse_obj(rule_d_0)
#     error = str(excinfo.value).split("\n")
#     assert error == ['1 validation error for Rule', 'search', "  title search option is set to True, it can't be index in full text: invalid integer. Set search option to False (type=value_error)"], error
#     # assert (error[0]) == "", error[0]

# def test_validation_error_005():
# rule_d_1 = {
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
#     r = Rule.parse_obj(rule_d_1)

# assert str(excinfo.value.split("\n")) == ["boo!"],excinfo.value.split("\n")


# def test_csv_import_005():
#     """test with csv file"""
#     rules = []
#     with open("test_rules.csv", "r") as f:
#         reader = DictReader(f, delimiter=",")
#         for row in reader:
#             rule_d = dict(row.items())
#             # for k, v in row.items():
#             #     rule_d[k] = cast_type_from_str_to_python(v)
#             r = Rule.parse_obj(rule_d)
#             rules.append(r)


def test_csv_import_008():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    c = CSVRuleImporter(fname)
    assert len(c.rules) == 52
