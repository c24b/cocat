import os
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