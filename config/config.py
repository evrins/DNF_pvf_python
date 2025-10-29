import pymysql
from loguru import logger
from pydantic import BaseModel


class DbConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str


_db_config = DbConfig(
    host='localhost',
    port=3306,
    # username='game',
    # password='uu5!^%jg',
    username='root',
    password='123456',
)


def get_db_config() -> DbConfig:
    return _db_config


def check_mysql_config(
        host: str,
        port: int,
        user: str,
        password: str,
) -> bool:
    conn = None
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            passwd=password,
            database='d_taiwan',
            connect_timeout=2,
        )

        conn.ping(True)

    except pymysql.Error as err:
        logger.error(f'error connecting to database: {err}')
        return False
    finally:
        if conn and conn.open:
            conn.close()
            logger.info('database connection closed')
            return True

    return False


def get_db_conn(db_name: str) -> pymysql.Connection:
    db_config = get_db_config()
    conn = pymysql.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.user,
        passwd=db_config.password,
        database=db_name,
        connect_timeout=2,
    )

    conn.ping(True)

    return conn


def get_current_account_id():
    return 18000000


def get_current_character_no():
    return 2


# todo build path from config


def get_stackable_parquet_file_path() -> str:
    return '/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/stackables.parquet'


def get_equipment_parquet_file_path() -> str:
    return '/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/equipments.parquet'


def get_magic_seal_parquet_file_path() -> str:
    return '/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/magic_seals.parquet'


def get_skill_parquet_file_path() -> str:
    return '/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/skills.parquet'


def get_orb_parquet_file_path() -> str:
    return '/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/orbs.parquet'
