from .model import Model
from .rule import Rule, CSVRuleImporter


def test_model_init_000():
    raw = CSVRuleImporter("./rules.csv")
    rules = raw.rules
    assert type(rules[0]) == Rule, type(rules[0])
    m = Model("dataset", rules)
    assert m.name == "dataset", m.name
    assert m.has_filter is True
    assert m.filters == {
        "accrual_periodicity": {
            "datatype": "string",
            "external_model": "reference",
            "reference": "ref_accrual_periodicity",
        },
        "has_georeference_dimension": {
            "datatype": "boolean",
            "external_model": None,
            "reference": None,
        },
        "is_open_data": {
            "datatype": "boolean",
            "external_model": None,
            "reference": None,
        },
        "license ": {
            "datatype": "string",
            "external_model": "reference",
            "reference": "ref_license",
        },
        "media_type": {
            "datatype": "string",
            "external_model": "reference",
            "reference": "ref_media_type",
        },
        "millesime": {"datatype": "integer", "external_model": None, "reference": None},
        "organizations": {
            "datatype": "object",
            "external_model": "organization",
            "reference": None,
        },
        "spatial_granularity": {
            "datatype": "string",
            "external_model": "reference",
            "reference": "ref_spatial_granularity",
        },
        "temporal": {"datatype": "integer", "external_model": None, "reference": None},
        "update_frequency": {
            "datatype": "string",
            "external_model": "reference",
            "reference": "ref_update_frequency",
        },
    }, m.filters
    assert m.reference_tables == [
        "ref_environment_detail",
        "ref_expositure_medium",
        "ref_env_agent_type",
        "ref_status",
        "ref_license",
        "ref_media_type",
        "ref_accrual_periodicity",
        "ref_update_frequency",
        "ref_spatial_granularity",
    ], m.reference_tables
