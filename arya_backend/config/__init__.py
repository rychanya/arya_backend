import os

# to get a string like this run:
# openssl rand -hex 32
AUT_SECRET_KEY = os.environ.get("AUT_SECRET_KEY")

AUT_ALGORITHM = os.environ.get("AUT_ALGORITHM")

AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES")
