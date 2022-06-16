from .model import Model
from .rule import Rule, CSVRuleImporter


def test_model_filter_000():
    raw = CSVRuleImporter("./rules.csv")
    rules = raw.rules
    assert type(rules[0]) == Rule, type(rules[0])
    m = Model("dataset", rules)
    assert m.name == "dataset", m.name
    m.get_filter_properties()
    assert m.has_filter is True
    assert m.filters == {
        "accrual_periodicity": {
            "datatype": "string",
            "external_model": "reference",
            "multiple": True,
            "reference": "ref_accrual_periodicity",
        },
        "has_georeference_dimension": {
            "datatype": "boolean",
            "external_model": None,
            "multiple": False,
            "reference": None,
        },
        "is_open_data": {
            "datatype": "boolean",
            "external_model": None,
            "multiple": False,
            "reference": None,
        },
        "license": {
            "datatype": "string",
            "external_model": "reference",
            "multiple": False,
            "reference": "ref_license",
        },
        "media_type": {
            "datatype": "string",
            "external_model": "reference",
            "multiple": True,
            "reference": "ref_media_type",
        },
        "millesime": {
            "datatype": "integer",
            "external_model": None,
            "multiple": True,
            "reference": None,
        },
        "organizations": {
            "datatype": "object",
            "external_model": "organization",
            "multiple": True,
            "reference": None,
        },
        "spatial_granularity": {
            "datatype": "string",
            "external_model": "reference",
            "multiple": False,
            "reference": "ref_spatial_granularity",
        },
        "temporal": {
            "datatype": "integer",
            "external_model": None,
            "multiple": False,
            "reference": None,
        },
        "update_frequency": {
            "datatype": "string",
            "external_model": "reference",
            "multiple": False,
            "reference": "ref_update_frequency",
        },
    }, m.filters
    assert sorted(m.reference_tables) == sorted(
        [
            "ref_environment_detail",
            "ref_expositure_medium",
            "ref_env_agent_type",
            "ref_status",
            "ref_license",
            "ref_media_type",
            "ref_accrual_periodicity",
            "ref_update_frequency",
            "ref_spatial_granularity",
        ]
    ), m.reference_tables


def test_model_index_001():
    raw = CSVRuleImporter("./rules.csv")
    rules = raw.rules
    assert type(rules[0]) == Rule, type(rules[0])
    m = Model("dataset", rules)
    assert m.name == "dataset", m.name
    m.get_index_properties()
    assert m.has_filter is True
    assert m.is_searchable is True
    assert sorted(list(m.index_mapping["en"]["properties"].keys())) == sorted(
        m.search_fields + m.filter_fields
    ), m.index_mapping["en"]["properties"].keys()


def test_model_build_002():
    """test building model properties"""
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    m.build_model()
    assert m.model_name == "Dataset"
    assert len(m.model_properties) == 27, len(m.model_properties)
    assert m.model_properties == [
        "environment_detail: List[str]= []",
        "expositure_medium: List[str]= []",
        "usage: Optional[List[str]]= []",
        "env_agent_type: List[str]= []",
        "env_agent_name: List[str]= []",
        "published: Optional[List[bool]]= []",
        "status: str= None",
        "issued: date= None",
        "modified: date= None",
        "title: str= None",
        "acronym: Optional[str]= None",
        "organizations: List[Organization]= []",
        "description: str= None",
        "access_url: str= None",
        "download_url: Optional[List[str]]= []",
        "contact_point: str= None",
        "is_open_data: Optional[bool]= None",
        "license: str= None",
        "media_type: Optional[List[str]]= []",
        "temporal: int= None",
        "millesime: Optional[List[int]]= []",
        "accrual_periodicity: Optional[List[str]]= []",
        "update_frequency: Optional[str]= None",
        "has_georeference_dimension: Optional[bool]= None",
        "spatial_coverage: Optional[List[str]]= []",
        "spatial_granularity: Optional[str]= None",
        "comment: Optional[str]= None",
    ], m.model_properties


def test_model_build_003():
    """test building model type filter"""
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    m.build_model("filter")
    assert m.model_name == "DatasetFilter"
    assert len(m.model_properties) == 10, len(m.model_properties)
    assert m.model_properties == [
        'organizations: List[Organization]= []',
        'is_open_data: Optional[bool]= None', 
        'license: str= None', 
        'media_type: Optional[List[str]]= []', 
        'temporal: int= None', 
        'millesime: Optional[List[int]]= []', 
        'accrual_periodicity: Optional[List[str]]= []',
        'update_frequency: Optional[str]= None',
        'has_georeference_dimension: Optional[bool]= None',
        'spatial_granularity: Optional[str]= None'], m.model_properties

def test_model_build_004():
    """test building model type multilang"""
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    m.build_model("multilang")
    assert m.model_name == "DatasetMultilang"
    assert len(m.model_properties) == 17, len(m.model_properties)
    assert m.model_properties == ['environment_detail: List[str]= []',
'expositure_medium: List[str]= []',
'usage: Optional[List[str]]= []',
'env_agent_type: List[str]= []',
'env_agent_name: List[str]= []',
'published: Optional[List[bool]]= []',
'title: str= None',
'acronym: Optional[str]= None',
'organizations: List[Organization]= []',
'description: str= None',
'license: str= None',
'accrual_periodicity: Optional[List[str]]= []',
'update_frequency: Optional[str]= None',
'has_georeference_dimension: Optional[bool]= None',
'spatial_coverage: Optional[List[str]]= []',
'spatial_granularity: Optional[str]= None',
'comment: Optional[str]= None'], m.model_properties

def test_model_external_models():
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    assert m.external_models == ["organization"], m.external_models
    assert m.has_external_models, m.has_external_models

def test_model_references():
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    assert m.has_references, m.has_references
    assert sorted(m.references) == sorted([('status', 'ref_status'),
('media_type', 'ref_media_type'),
('update_frequency', 'ref_update_frequency'),
('accrual_periodicity', 'ref_accrual_periodicity'),
('spatial_granularity', 'ref_spatial_granularity'),
('license', 'ref_license'),
('expositure_medium', 'ref_expositure_medium'),
('env_agent_type', 'ref_env_agent_type'),
('environment_detail', 'ref_environment_detail')]), m.references

def test_is_multilang():
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    assert m.is_multilang, [r.translation for r in m.rules]

def test_is_searchable():
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    assert m.is_searchable, [r.search for r in m.rules]

def test_has_filter():
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    assert m.has_filter, [r.filter for r in m.rules]

def test_write_modelfiles():
    raw = CSVRuleImporter("./rules.csv")
    m = Model("dataset", raw.rules)
    assert len(m.types) == 3, m.types
    m.write_model()