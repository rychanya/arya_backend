import os

import nox
from dotenv import load_dotenv

nox.options.sessions = ["prety"]


@nox.session(py=False)
def serv(session: nox.Session):
    load_dotenv()
    # session.log(os.path.dirname(__file__))
    session.install(".")
    # session.log(os.environ.get("MONGO_USER"))
    session.run(
        "uvicorn",
        "arya_backend.main:app",
        "--reload",
        env={  # type: ignore
            "AUT_ALGORITHM": os.environ.get("AUT_ALGORITHM"),
            "AUTH_ACCESS_TOKEN_EXPIRE_MINUTES": os.environ.get(
                "AUTH_ACCESS_TOKEN_EXPIRE_MINUTES"
            ),
            "AUT_SECRET_KEY": os.environ.get("AUT_SECRET_KEY"),
            "MONGO_DB_NAME": os.environ.get("MONGO_DB_NAME"),
            "MONGO_PASSWORD": os.environ.get("MONGO_PASSWORD"),
            "MONGO_USER": os.environ.get("MONGO_USER"),
        },
    )


@nox.session
def req(session: nox.Session):
    session.run(
        "poetry",
        "export",
        "-f",
        "requirements.txt",
        "--without-hashes",
        "--output",
        "requirements.txt",
        external=True,
    )


@nox.session
def deploy(session: nox.Session):
    session.run(
        "poetry",
        "export",
        "-f",
        "requirements.txt",
        "--without-hashes",
        "--output",
        "requirements.txt",
        external=True,
    )
    session.run("git", "push", "heroku", "master", external=True)


@nox.session(py=False)
def prety(session: nox.Session):
    session.run("isort", ".", external=True)
    session.run("black", ".", external=True)
    session.run("flake8", "arya_backend/", external=True)
