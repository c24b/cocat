
from .reference import Reference, CSVReferenceImporter


def test_reference_001():
    header = ["name_en","name_fr","uri","slug", "table_name"]
    value = ["Triennial","Triannuel","http://purl.org/dc/terms/acrualPeriodicity#Triennial","triennial", "ref_temporal"]
    ref_d = dict(zip(header, value))
    r = Reference.parse_obj(ref_d)
    r.set_name("fr")
    assert r.name_en == "Triennial"
    assert r.name_fr == "Triannuel"
    assert r.name == "Triannuel"
    assert r.table_name == "ref_temporal"
    assert r.field == "temporal"