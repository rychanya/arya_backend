import nox

nox.options.sessions = ["prety"]


@nox.session
def serv(session: nox.Session):
    session.install(".")
    session.run("uvicorn", "arya_backend.main:app", "--reload")


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
    session.run("git", "push", "heroku", "master")


@nox.session(py=False)
def prety(session: nox.Session):
    session.run("black", ".", external=True)
    session.run("isort", ".", external=True)
