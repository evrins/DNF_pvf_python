from pydantic import BaseModel


class DbConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str


_db_config = DbConfig(
    host='localhost',
    port=3306,
    username='game',
    password='uu5!^%jg',
)


def get_db_config() -> DbConfig:
    return _db_config
