from sqlalchemy import select

from config.config import get_db_config
from dnfpkgtool.db.db_manager import DBManager
from dnfpkgtool.db.model import CharacterInfo


def test_query():
    db_config = get_db_config()
    dbm = DBManager(db_config)
    with dbm.get_session('taiwan_cain') as sess:
        stmt = select(CharacterInfo)
        for charac in sess.scalars(stmt):
            print(charac.__dict__)
