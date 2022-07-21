#!/usr/bin/env python3.9


import os
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from beanie import init_beanie

from settings import settings 

{%for app_name in apps%}
from apps.{{app_name}}.routers import router as {{app_name}}_router{%endfor%}
{%for app_name, model_names in models%}
from apps.{{app_name}}.models import {{model_names|join(", ")}}{%endfor%}

app = FastAPI()

origins = [
    settings.FRONT_URI,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URI)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    await init_beanie(database=app.mongodb, document_models=[{{docs}}])
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


{%for model_name in apps%}
app.include_router({{model_name}}_router, tags=["{{model_name}}s"], prefix="/{{model_name}}"){%endfor%}


@app.get("/")
async def root():
    response = RedirectResponse(url='/docs')
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.BACK_URL, port=settings.BACK_PORT, reload=settings.RELOAD, debug=settings.DEBUG, workers=settings.WORKERS_NB)