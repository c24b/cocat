#!/usr/bin/.venv/python3

from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, HttpUrl, EmailStr
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from datetime import date
from pydantic import BaseModel, Field,  HttpUrl, EmailStr,  constr, validator
from apps.organization.models import Organization
from apps.reference.routers import get_reference_values

def check_value_in_set(cls, v, values, field):
    lang = values.get('lang')
    if lang:
        ref_values = get_reference_values(field.name, lang)
        accepted_values = ",".join([repr(e) for e in ref_values])
        if v not in ref_values: 
            raise ValueError(f"{field.name} must be one of [{accepted_values}]")
    return v

def check_multiple_values_in_set(cls, v, values, field):
    lang = values.get('lang')
    if lang:
        ref_values = get_reference_values(field.name, lang)
        accepted_values = ",".join([repr(e) for e in ref_values])
        if not set(v).issubset(ref_values):  
            raise ValueError(f"{field.name} must be one of [{accepted_values}]")
    return v

class DatasetFilter(BaseModel)
    organizations: List[Organization]= []
    is_open_data: Optional[bool]= None
    license: str= None
    media_type: Optional[List[str]]= []
    temporal: int= None
    millesime: Optional[List[int]]= []
    accrual_periodicity: Optional[List[str]]= []
    update_frequency: Optional[str]= None
    has_georeference_dimension: Optional[bool]= None
    spatial_granularity: Optional[str]= None
    _value_in_set = validator('ref_environment_detail', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_expositure_medium', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_env_agent_type', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_status', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_license', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_media_type', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_accrual_periodicity', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_update_frequency', allow_reuse=True)(check_multiple_values_in_set)
    _value_in_set = validator('ref_spatial_granularity', allow_reuse=True)(check_multiple_values_in_set)
    
    class Config:
        schema_extra = {
            "example": {'organizations': 'INERIS|CEREMA', 'is_open_data': 'True', 'license': 'N/D', 'media_type': 'xls|pdf', 'temporal': '(2007-01-01, 2022-03-29)', 'millesime': '[2001, 2002, 2007, 2008,2009, 2018, 2019,2020, 2021, 2022]', 'accrual_periodicity': 'mensuel| trimestriel', 'update_frequency': 'mensuel| trimestriel', 'has_georeference_dimension': '1', 'spatial_granularity': 'POI| Latitude/Longitude'}
        }