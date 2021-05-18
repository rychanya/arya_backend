import nox

nox.options.sessions = ["serv"]


@nox.session
def serv(session: nox.Session):
    session.install(".")
    session.run("uvicorn", "arya_backend.main:app", "--reload")

@nox.session
def deploy(session: nox.Session):
    session.run('poetry', 'export', '-f', 'requirements.txt', '--without-hashes', '--output', 'arya_backend/requirements.txt', external=True)
    session.run('deta', 'deploy', external=True)
