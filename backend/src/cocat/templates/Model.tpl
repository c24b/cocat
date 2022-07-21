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
{%if has_external_models%}{%for ext_model in external_models %}{{ext_model}}{%endfor%}{%endif%}
{%if has_vocabulary%}from apps.vocabulary.routers import get_reference_values

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
{%endif%}
class {{model_name}}(BaseModel)
    {%for value in model_properties %}{{value}}
    {%endfor%}{%if has_vocabulary%}{% for reference in references %}_value_in_set = validator('{{reference[1]}}', allow_reuse=True){% if not reference[0] %}(check_value_in_set){% else %}(check_multiple_values_in_set){%endif%}
    {%endfor%}{%endif%}
    class Config:
        schema_extra = {
            "example": {{example}}
        }
