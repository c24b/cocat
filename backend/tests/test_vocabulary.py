import os
from cocat.reference import Reference
from cocat.vocabulary import Vocabulary
from cocat.db import DB
from csv import DictReader

def test_vocabulary_000_init_with_csv():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr", csv_file=fname)
    assert v.name == "environment"
    assert v.lang == "fr"
    assert v.labels ==  ['Air', 'Eau', 'Sols', 'Alimentation'], v.labels
    assert v.names_fr == v.labels
    assert len(v.references) == 4, len(v.references)
    assert list(v.references[0].__dict__.keys()) == [
        'id','vocabulary',
        'name_en',
        'name_fr',
        'uri',
        'slug',
        'lang',
        'updated',
        'standards',
        '_id'], list(v.references[0].__dict__.keys())
    v.delete()

def test_vocabulary_000_init_with_jsonl():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    with open(fname, "r") as f:
        reader = DictReader(f, delimiter=",")
        references = []
        for row in reader:
            row["file"] = os.path.basename(fname)
            row["vocabulary"] = "environment"
            row["lang"] = "fr"
            references.append(row)
    assert references[0] == {'file': 'test_ref_environment.csv', 'lang': 'fr', 'name_en': 'Air', 'name_fr': 'Air', 'slug': 'air','uri': 'http://dcat-ap.ch/vocabulary/themes/air','vocabulary': 'environment'}, references[0]
    v = Vocabulary(name="environment", lang="fr", references=references)
    assert v.name == "environment"
    assert v.lang == "fr"
    assert v.labels ==  ['Air', 'Eau', 'Sols', 'Alimentation'], v.labels
    assert v.names_fr == v.labels
    assert len(v.references) == 4, len(v.references)
    assert list(v.references[0].__dict__.keys()) == [
        'id','vocabulary',
        'name_en',
        'name_fr',
        'uri',
        'slug',
        'lang',
        'updated',
        'standards'], list(v.references[0].__dict__.keys())
    v.delete()

def test_vocabulary_001_existing_voc():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr", csv_file=fname)
    assert v.exists, v.exists
    v.delete()
    assert v.references is None, v.references
    v2 = Vocabulary(name="environment", lang="fr")
    assert v2.references is not None

def test_vocabulary_002_default_lang():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr", csv_file=fname)
    # v.create(csv_file=fname)
    assert v.filename == os.path.basename(fname)
    assert len(v.references) == 4, len(v.references)
    assert sorted(v.labels) == sorted(['Air', 'Eau', 'Sols', 'Alimentation']), v.labels
    assert v.names_en == ['Air', 'Water', 'Soils', 'Food'], v.names_en
    assert v.names_fr == v.labels, v.labels
    assert v.uris == ['http://dcat-ap.ch/vocabulary/themes/air',
                      'http://dcat-ap.ch/vocabulary/themes/water',
                      'http://dcat-ap.ch/vocabulary/themes/soil',
                      'http://dcat-ap.ch/vocabulary/themes/food'], v.uris
    assert v.labels == v.names_fr, v.labels
    v.delete()

def test_vocabulary_002_get_refs():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr")
    v.create(csv_file=fname)
    references = v.get_references()
    assert len(references) == 4, references
    assert isinstance(references[0], Reference)
    assert references[0].vocabulary == "environment", references[0].vocabulary
    v.delete()

def test_voc_003_get_labels():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr")
    v.create(csv_file=fname)
    labels_fr = v.get_labels_by_lang("fr")
    assert labels_fr == ['Air', 'Eau', 'Sols', 'Alimentation'], labels_fr
    labels_en = v.get_labels_by_lang("en")
    assert labels_en == ['Air', 'Water', 'Soils', 'Food'], labels_en
    v.delete()  

def test_voc_004_get_previous_refs():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr")
    v.delete()
    v.create(csv_file=fname)
    v2 = Vocabulary(name="environment", lang="en")
    assert len(v2.references) == 4
    v.delete()
    assert DB.reference.count_documents({"vocabulary": "environment"}) == 0, DB.reference.count_documents({"vocabulary": "environment"})

def test_voc_005_declared_csv():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="en", csv_file=fname)
    assert len(v.references) == 4
    assert v.labels == ['Air', 'Water', 'Soils', 'Food'], v.labels
    v.delete()