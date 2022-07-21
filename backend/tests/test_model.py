import os
from cocat.model import Model, FilterModel, MultiLangModel
from cocat.config_model import CSVConfig 
from cocat.property import Property

def test_csv_config_model_init_000():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    # assert fname == "tests/rules", fname
    raw = CSVConfig(fname)
    assert len(raw.models) == 6, len(raw.models)
    assert list(raw.models.keys()) == ['dataset', 'organization', 'user', 'vocabulary', 'comment', 'license'], list(raw.models.keys())
    dataset_model_a = raw.models["dataset"]
    assert len(dataset_model_a.properties) == 27, len(dataset_model_a.properties)
    assert len(dataset_model_a.vocabularies) == 7, len(dataset_model_a.vocabularies)
    assert len(dataset_model_a.external_models) == 1, len(dataset_model_a.external_models)
    assert dataset_model_a.is_multilang, dataset_model_a.is_multilang
    assert dataset_model_a.has_filter, dataset_model_a.has_filter
    assert dataset_model_a.is_searchable, dataset_model_a.is_searchable
    assert dataset_model_a.has_index, dataset_model_a.has_index
    rules = [r for r in raw.properties if r.model == "dataset"]
    assert len(rules) == 27
    dataset_model_b = Model("dataset", rules)
    assert len(dataset_model_b.properties) == 27, len(dataset_model_b.properties)
    assert len(dataset_model_b.vocabularies) == 7, len(dataset_model_b.vocabularies)
    
def test_model_properties_001():
    pass
def test_model_vocabularies_002():
    pass

def test_model_multilang_003():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    # assert fname == "tests/rules", fname
    raw = CSVConfig(fname)
    dataset_model_a = raw.models["dataset"]
    assert list(dataset_model_a.multilang.keys()) == [
    'environment_detail',
    'expositure_medium',
    'usage',
    'env_agent_type',
    'env_agent_name',
    'published',
    'title',
    'acronym',
    'organizations',
    'description',
    'license',
    'accrual_periodicity',
    'update_frequency',
    'has_geo_dimension',
    'spatial_coverage',
    'spatial_granularity',
    'comment']

def test_model_filters_004():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    # assert fname == "tests/rules", fname
    raw = CSVConfig(fname)
    dataset_model_a = raw.models["dataset"]
    assert dataset_model_a.filters["has_geo_dimension"] == {'datatype': 'boolean',
                      'external_model': None,
                      'external_model_display_keys': None,
                      'is_external_model': False,
                      'is_multiple': False,
                      'is_vocabulary': False,
                      'vocabulary': None}, dataset_model_a.filters["has_geo_dimension"]

def test_model_vocabularies_005():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    raw = CSVConfig(fname)
    a_model = Model("dataset", [r for r in raw.properties if r.model == "dataset"])
    assert a_model.has_vocabulary, a_model.has_vocabulary
    assert len(a_model.vocabularies) == 7,len(a_model.vocabularies) 
    assert list(a_model.vocabularies.keys()) ==  [
        'environment_detail',
        'status',
        'license',
        'media_type',
        'accrual_periodicity',
        'update_frequency',
        'spatial_granularity'], list(a_model.vocabularies.keys())
    assert list(a_model.vocabularies["license"]["names_en"]) == [
        'CC-BY-NC-SA',
        'CC0',
        'Open License',
        'Open License Etalab',
        'SINP',
        'Not Specified',
        'OdbL'], a_model.vocabularies["license"]["names_en"]


# def test_model_index_007():
#     '''test indexing'''
#     fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
#     raw = CSVConfig(fname)
#     properties = raw.properties
#     assert type(properties[0]) == Property, type(properties[0])
#     m = Model("dataset", properties)
#     assert m.name == "dataset", m.name
#     assert m.has_filter is True
#     assert m.is_searchable is True
#     assert sorted(list(m.mapping["en"]["properties"].keys())) == sorted(
#         list(m.search.keys()) + list(m.filters.keys())
#     ), m.index["en"]["properties"].keys()
#     assert list(m.mapping['fr']["properties"].values()) == None, list(m.mapping['fr']["properties"].values())

def test_model_build_008():
    """test building model properties"""
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    raw = CSVConfig(fname)
    m = Model("dataset", [r for r in raw.properties if r.model== "dataset"])
    assert m.model_name == "Dataset"
    assert len(m.properties) == 27, len(m.properties)
    assert m.pydantic_model == [
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
        "has_geo_dimension: Optional[bool]= None",
        "spatial_coverage: Optional[List[str]]= []",
        "spatial_granularity: Optional[str]= None",
        "comment: Optional[str]= None",
    ], m.pydantic_model

def test_model_write_008():
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    raw = CSVConfig(fname)
    dataset_model_a = raw.models["dataset"]
    dataset_model_a.write_model()
    dataset_model_a.write_router()
def test_model_build_filter_009():
    """test building model type filter"""
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    raw = CSVConfig(fname)
    m = FilterModel("dataset", [r for r in raw.properties if r.model== "dataset"])
    assert m.model_name == "DatasetFilter"
    assert len(m.properties) == 10, len(m.properties)
    assert m.pydantic_model == [
        'organizations: List[Organization]= []',
        'is_open_data: Optional[bool]= None', 
        'license: str= None', 
        'media_type: Optional[List[str]]= []', 
        'temporal: int= None', 
        'millesime: Optional[List[int]]= []', 
        'accrual_periodicity: Optional[List[str]]= []',
        'update_frequency: Optional[str]= None',
        'has_geo_dimension: Optional[bool]= None',
        'spatial_granularity: Optional[str]= None'], m.pydantic_model

def test_model_build_multilang_010():
    """test building model type multilang"""
    fname = os.path.join(os.path.dirname(__file__), 'rules.csv')
    raw = CSVConfig(fname)
    m = MultiLangModel("dataset", [r for r in raw.properties if r.model== "dataset"])
    assert m.model_name == "DatasetMultiLang"
    assert len(m.properties) == 17, len(m.model_properties)
    assert m.pydantic_model == ['environment_detail: List[str]= []',
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
'has_geo_dimension: Optional[bool]= None',
'spatial_coverage: Optional[List[str]]= []',
'spatial_granularity: Optional[str]= None',
'comment: Optional[str]= None'], m.pydantic_model

# def test_model_external_models():
#     fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
#     raw = CSVPropertyImporter(fname)
#     m = Model("dataset", raw.properties)
#     assert m.external_models == ["organization"], m.external_models
#     assert m.has_external_models, m.has_external_models

# def test_model_references():
#     fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
#     raw = CSVPropertyImporter(fname)
#     m = Model("dataset", raw.properties)
#     assert m.has_references, m.has_references
#     assert sorted(m.references) == sorted([('status', 'ref_status'),
# ('media_type', 'ref_media_type'),
# ('update_frequency', 'ref_update_frequency'),
# ('accrual_periodicity', 'ref_accrual_periodicity'),
# ('spatial_granularity', 'ref_spatial_granularity'),
# ('license', 'ref_license'),
# ('expositure_medium', 'ref_expositure_medium'),
# ('env_agent_type', 'ref_env_agent_type'),
# ('environment_detail', 'ref_environment_detail')]), m.references

# def test_is_multilang():
#     fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
#     raw = CSVPropertyImporter(fname)
#     m = Model("dataset", raw.properties)
#     assert m.is_multilang, [r.translation for r in m.properties]

# def test_is_searchable():
#     fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
#     raw = CSVPropertyImporter(fname)
#     m = Model("dataset", raw.properties)
#     assert m.is_searchable, [r.search for r in m.properties]

# def test_has_filter():
#     fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
#     raw = CSVPropertyImporter(fname)
#     m = Model("dataset", raw.properties)
#     assert m.has_filter, [r.filter for r in m.properties]

# def test_write_modelfiles():
#     fname = os.path.join(os.path.dirname(__file__), 'properties.csv')
#     raw = CSVPropertyImporter(fname)
#     m = Model("dataset", raw.properties)
#     assert len(m.types) == 3, m.types
#     m.write_model()