from config.config import get_db_config
from dnfpkgtool.db.db_manager import DBManager
from dnfpkgtool.db.repo import CharacterInfoRepo


def test_query_all_characters():
    db_config = get_db_config()
    dbm = DBManager(db_config)
    repo = CharacterInfoRepo(dbm.get_engine('taiwan_cain'))
    for character in repo.query_all_character_info_list():
        print(character.__dict__)
