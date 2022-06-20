import warnings
import pytest
import os
from cocat.reference import Reference, CSVReferenceImporter
from cocat.db import DB


def test_reference_001():
    header = ["name_en", "name_fr", "uri", "slug", "table_name"]
    value = [
        "Triennial",
        "Triannuel",
        "http://purl.org/dc/terms/acrualPeriodicity#Triennial",
        "triennial",
        "ref_temporal",
    ]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)
    # r.set_name("fr")
    assert r.name_en == "Triennial"
    assert r.name_fr == "Triannuel"
    assert r.name == "Triannuel"
    assert r.table_name == "ref_temporal"
    assert r.field == "temporal"


def test_reference_002_lang():
    header = ["name_en", "name_fr", "uri", "slug", "table_name", "lang"]
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
    assert r.table_name == "ref_temporal"
    assert r.field == "temporal"


def test_reference_003_store():
    header = ["name_en", "name_fr", "uri", "slug", "table_name", "lang"]
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
    # assert r._id is not None, r._id
    # assert r._id.isinstance(ObjectId) == None, r._id

def test_reference_004_store_if_not_exists():
    header = ["name_en", "name_fr", "uri", "slug", "table_name", "lang"]
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
    ## catch logging
    # assert 'Something bad happened!' in r.add().text
   
def test_reference_005_delete():
    header = ["name_en", "name_fr", "uri", "slug", "table_name", "lang"]
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
    r.delete()
    ## catch logging
    # assert 'Something bad happened!' in r.add().text

def test_reference_006_insert_from_csv():
    DB.reference.delete_many({"table_name": "test_environment"})
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    assert "backend/tests" in fname, fname
    c = CSVReferenceImporter(fname)
    assert len(c.references) == 4
    assert DB.reference.count_documents({"table_name": "test_environment"}) == 4, DB.references.find({"table_name": "test_environment"})
    DB.reference.delete_many({"table_name": "test_environment"})
