from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arya_backend.routers import auth, qa, upload

app = FastAPI()


origins = ["https://kittyanswers.herokuapp.com", "http://localhost:8080"]
# origins = ["*"]


app.include_router(auth.router)
app.include_router(qa.router)
app.include_router(upload.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)
