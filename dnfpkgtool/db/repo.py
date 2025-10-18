from sqlalchemy import select
from sqlalchemy.orm import Session

from dnfpkgtool.db.model import CharacterInfo


class CharacterInfoRepo:
    def __init__(self, engine):
        self.engine = engine

    def query_all_character_info_list(self):
        with Session(self.engine) as session:
            stmt = select(CharacterInfo)
            return session.scalars(stmt).all()
