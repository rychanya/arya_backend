from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arya_backend.routers import auth
import os

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

@app.get('/')
def index():
    return os.environ.get('API')