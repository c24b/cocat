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

class DatasetMultilang(BaseModel)
    environment_detail: List[str]= []
    expositure_medium: List[str]= []
    usage: Optional[List[str]]= []
    env_agent_type: List[str]= []
    env_agent_name: List[str]= []
    published: Optional[List[bool]]= []
    title: str= None
    acronym: Optional[str]= None
    organizations: List[Organization]= []
    description: str= None
    license: str= None
    accrual_periodicity: Optional[List[str]]= []
    update_frequency: Optional[str]= None
    has_georeference_dimension: Optional[bool]= None
    spatial_coverage: Optional[List[str]]= []
    spatial_granularity: Optional[str]= None
    comment: Optional[str]= None
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
            "example": {'environment_detail': 'N/D', 'expositure_medium': 'N/D', 'usage': '[“cancer”, “chlordécone”, “O3”, “N2”, “Azote” ]', 'env_agent_type': 'N/D', 'env_agent_name': '["NVDI", "Azote","O3", "N2","chlordécone"]', 'published': 'TRUE', 'title': 'Base de données des adresses nationales', 'acronym': 'BAN ', 'organizations': 'INERIS|CEREMA', 'description': 'Ce jeu de données contient une liste d’équipement sportifs décrit par leur nom, leurs coordonnées postales et leur géolocalisation ainsi que par la liste des activités sportives qui peuvent y être pratiquées', 'license': 'N/D', 'accrual_periodicity': 'mensuel| trimestriel', 'update_frequency': 'mensuel| trimestriel', 'has_georeference_dimension': '1', 'spatial_coverage': 'IDF|HDF|Marseille', 'spatial_granularity': 'POI| Latitude/Longitude', 'comment': ''}
        }