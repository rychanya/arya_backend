from itertools import cycle

from pydantic import BaseModel, HttpUrl


class User(BaseModel):
    login: str
    password: str


class Settings(BaseModel):
    users: list[User]
    urls: list[HttpUrl]
    headless: bool = False

    @property
    def users_cycle(self):
        return cycle(self.users)


class Counter(BaseModel):
    passed: int
    failed: int
    unanswered: int
