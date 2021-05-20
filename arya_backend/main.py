import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arya_backend.db import client
from arya_backend.routers import auth, qa

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(qa.router)


@app.get("/")
def index():
    return client.list_database_names()
