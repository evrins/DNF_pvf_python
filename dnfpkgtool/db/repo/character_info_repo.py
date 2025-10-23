from sqlalchemy import select
from sqlalchemy.orm import Session

from dnfpkgtool.db.model.character_info import CharacterInfo
from dnfpkgtool.db.repo.base_repo import BaseRepo


class CharacterInfoRepo(BaseRepo):
    def __init__(self):
        super().__init__('taiwan_cain')

    def query_all_character_info_list(self):
        with Session(self.get_engine()) as session:
            stmt = select(CharacterInfo)
            return session.scalars(stmt).all()
