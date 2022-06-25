import os
from cocat.reference import Reference
from cocat.vocabulary import Vocabulary

def test_vocabulary_001():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr")
    v.delete()
    v.create(csv_file=fname)
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
    v.delete()
    v.create(csv_file=fname)
    references = v.get_references()
    assert len(references) == 4, references
    assert isinstance(references[0], Reference)
    assert references[0].vocabulary == "environment", references[0].vocabulary
    v.delete()

def test_voc_003_get_labels():
    fname = os.path.join(os.path.dirname(__file__), 'test_ref_environment.csv')
    v = Vocabulary(name="environment", lang="fr")
    v.delete()
    v.create(csv_file=fname)
    labels_fr = v.get_labels_by_lang("fr")
    assert labels_fr == ['Air', 'Eau', 'Sols', 'Alimentation'], labels_fr
    labels_en = v.get_labels_by_lang("en")
    assert labels_en == ['Air', 'Water', 'Soils', 'Food'], labels_en