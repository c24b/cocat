#!/usr/bin/env python3

import os
from pydantic import BaseSettings, Field, SecretStr
from typing import Optional


class Settings(BaseSettings):
    LANGUAGES: list = os.environ.get("LANGUAGES").split(",")
    DEBUG: Optional[bool] = os.environ.get("DEBUG")
    DB_URI: str = os.environ.get("DB_URI")
    FRONT_URI: str = os.environ.get("FRONT_URL")
    BACK_URI: str = os.environ.get("BACK_URI")
    DB_NAME:str = os.environ.get("DB_NAME")
    ES_URI:str = os.environ.get("ES_URI")
    API_RELOAD: Optional[bool] = True
    class Config:
        env_file = ".env"
settings = Settings()

