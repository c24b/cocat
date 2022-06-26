import os
from cocat.model import Model
from cocat.property import Property, CSVPropertyImporter 


def test_model_filter_000():
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    properties = raw.properties
    assert type(properties[0]) == Property, type(properties[0])
    m = Model("dataset", properties)
    assert m.name == "dataset", m.name
    assert m.has_filter is True
    assert m.filter_properties == {
        "accrual_periodicity": {
            "datatype": "string",
            "external_model": "vocabulary",
            "multiple": True,
            "vocabulary": "ref_accrual_periodicity",
        },
        "has_georeference_dimension": {
            "datatype": "boolean",
            "external_model": None,
            "multiple": False,
            "vocabulary": None,
        },
        "is_open_data": {
            "datatype": "boolean",
            "external_model": None,
            "multiple": False,
            "vocabulary": None,
        },
        "license": {
            "datatype": "string",
            "external_model": "vocabulary",
            "multiple": False,
            "vocabulary": "ref_license",
        },
        "media_type": {
            "datatype": "string",
            "external_model": "vocabulary",
            "multiple": True,
            "vocabulary": "ref_media_type",
        },
        "millesime": {
            "datatype": "integer",
            "external_model": None,
            "multiple": True,
            "vocabulary": None,
        },
        "organizations": {
            "datatype": "object",
            "external_model": "organization",
            "multiple": True,
            "vocabulary": None,
        },
        "spatial_granularity": {
            "datatype": "string",
            "external_model": "vocabulary",
            "multiple": False,
            "vocabulary": "ref_spatial_granularity",
        },
        "temporal": {
            "datatype": "integer",
            "external_model": None,
            "multiple": False,
            "vocabulary": None,
        },
        "update_frequency": {
            "datatype": "string",
            "external_model": "vocabulary",
            "multiple": False,
            "vocabulary": "ref_update_frequency",
        },
    }, m.filters
    assert sorted(m.vocabulary_tables) == sorted(
        [
            "environment_detail",
            "expositure_medium",
            "env_agent_type",
            "status",
            "license",
            "media_type",
            "accrual_periodicity",
            "update_frequency",
            "spatial_granularity",
        ]
    ), m.vocabulary_tables


def test_model_index_001():
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    properties = raw.properties
    assert type(properties[0]) == Property, type(properties[0])
    m = Model("dataset", properties)
    assert m.name == "dataset", m.name
    assert m.has_filter is True
    assert m.is_searchable is True
    assert sorted(list(m.index_mapping["en"]["properties"].keys())) == sorted(
        list(m.search_properties.keys()) + list(m.filter_properties.keys())
    ), m.index_mapping["en"]["properties"].keys()


def test_model_build_002():
    """test building model properties"""
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
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
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
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
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
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
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
    assert m.external_models == ["organization"], m.external_models
    assert m.has_external_models, m.has_external_models

def test_model_references():
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
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
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
    assert m.is_multilang, [r.translation for r in m.properties]

def test_is_searchable():
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
    assert m.is_searchable, [r.search for r in m.properties]

def test_has_filter():
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
    assert m.has_filter, [r.filter for r in m.properties]

def test_write_modelfiles():
    fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
    raw = CSVPropertyImporter(fname)
    m = Model("dataset", raw.properties)
    assert len(m.types) == 3, m.types
    m.write_model()