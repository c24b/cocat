import warnings
import pytest
import os
from cocat.reference import Reference
from cocat.db import DB
from csv import DictReader


def test_reference_001():
    header = ["name_en", "name_fr", "uri", "slug", "vocabulary"]
    value = [
        "Triennial",
        "Triannuel",
        "http://purl.org/dc/terms/acrualPeriodicity#Triennial",
        "triennial",
        "ref_temporal",
    ]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)
    assert r.name_en == "Triennial"
    assert r.name_fr == "Triannuel"
    assert r.name == "Triannuel"
    assert r.vocabulary == "ref_temporal"
    assert r.field == "temporal"


def test_reference_002_lang():
    header = ["name_en", "name_fr", "uri", "slug", "vocabulary", "lang"]
    value = [
        "Triennial",
        "Triannuel",
        "http://purl.org/dc/terms/acrualPeriodicity#Triennial",
        "triennial",
        "ref_temporal",
        "en",
    ]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)

    assert r.name_en == "Triennial"
    assert r.name_fr == "Triannuel"
    assert r.name == "Triennial"
    assert r.vocabulary == "ref_temporal"
    assert r.field == "temporal"


def test_reference_003_store():
    header = ["name_en", "name_fr", "uri", "slug", "vocabulary", "lang"]
    value = [
        "Triennial",
        "Triannuel",
        "http://purl.org/dc/terms/acrualPeriodicity#Triennial",
        "triennial",
        "ref_temporal",
        "en",
    ]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)
    r.add()
    assert r.id is not None, r.id
    r.delete()
    # assert r._id is not None, r._id
    # assert r._id.isinstance(ObjectId) == None, r._id


def test_reference_004_store_if_not_exists():
    header = ["name_en", "name_fr", "uri", "slug", "vocabulary", "lang"]
    value = [
        "Triennial",
        "Triannuel",
        "http://purl.org/dc/terms/acrualPeriodicity#Triennial",
        "triennial",
        "ref_temporal",
        "en",
    ]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)
    r.add()
    r.delete()
    # catch logging
    # assert 'Something bad happened!' in r.add().text


def test_reference_005_delete():
    header = ["name_en", "name_fr", "uri", "slug", "vocabulary", "lang"]
    value = [
        "Triennial",
        "Triannuel",
        "http://purl.org/dc/terms/acrualPeriodicity#Triennial",
        "triennial",
        "ref_temporal",
        "en",
    ]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)
    r.add()
    r.delete()
    # catch loggingfile_
    # assert 'Something bad happened!' in r.add().text

def test_reference_006_update():
    header = ["name_en", "name_fr", "uri", "slug", "vocabulary", "lang"]
    value = [
        "Triennial",
        "Triannuel",
        "http://purl.org/dc/terms/acrualPeriodicity#Triennial",
        "triennial",
        "ref_temporal",
        "en",
    ]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)
    r.add()
    new_value = {"name_fr": "Semestrielle"}
    r.update(new_value)
    assert r.name_fr == "Semestrielle"
    r.delete()

def test_reference_007_find_by_name():
    DB.reference.drop()
    r = Reference
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    with open(fname, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            row["file"] = os.path.basename(fname)
            row["vocabulary"] = "environment"
            row["lang"] = "en"
            r = Reference.parse_obj(row)
            r.delete()
            r.add()
        
    assert DB.reference.count_documents({"vocabulary": "environment"}) == 4 
    assert DB.reference.distinct("name_fr") == ['Air', 'Alimentation', 'Eau', 'Sols']
    ref = Reference(name="test", lang="fr")
    new_ref = ref.get_by_label("Food")
    assert new_ref["name_fr"] == "Alimentation", new_ref["name_fr"]
    assert new_ref["name_en"] == "Food", new_ref["name_en"]
    assert new_ref["uri"] == "http://dcat-ap.ch/vocabulary/themes/food", new_ref["uri"]
    new_ref2 = ref.get_by_label("Alimentation")
    assert new_ref == new_ref2
    assert new_ref2["name_fr"] == "Alimentation", new_ref2
    assert new_ref2["name_en"] == "Food", new_ref2["name_en"]
    assert new_ref2["uri"] == "http://dcat-ap.ch/vocabulary/themes/food", new_ref2["uri"]
    DB.reference.delete_many({"vocabulary": "environment"})