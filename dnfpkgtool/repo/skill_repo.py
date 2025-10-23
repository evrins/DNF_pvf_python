from pathlib import Path
from typing import Dict, List

import polars as pl

from config import config
from dnfpkgtool.pvf.pvf_reader import PVFReader
from dnfpkgtool.repo import MappingElementLocation, remapping_pvf_list


def build_skill_repo_parquet(pvf_list: List[Dict[str, any]], fp: str):
    mappings = [
        ('job', 'job', 0, MappingElementLocation.First),
        ('name', '[name]', '', MappingElementLocation.First),
        ('name2', '[name2]', '', MappingElementLocation.First),
        ('basic_explain', '[basic explain]', '', MappingElementLocation.First),
        ('explain', '[explain]', '', MappingElementLocation.First),
        (
            'feature_skill_index',
            '[feature skill index]',
            0,
            MappingElementLocation.First,
        ),
        ('skill_class', '[skill class]', 0, MappingElementLocation.First),
    ]
    df = remapping_pvf_list(pvf_list, mappings)
    df = pl.DataFrame(df)

    df.write_parquet(fp)


base_dir = Path(__file__).parent


def test_build_skill_repo_parquet():
    pvf_path = '/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf'
    reader = PVFReader(pvf_path)
    stackable_dict = reader.get_skill_list()
    build_skill_repo_parquet(stackable_dict, base_dir / 'data' / 'skills.parquet')


def test_query():
    fp = base_dir / 'data' / 'items.parquet'
    skill_repo = SkillRepo(str(fp))
    rs = skill_repo.query('药')
    print(len(rs))


class SkillRepo:
    def __init__(self, fp: str):
        self.df = pl.read_parquet(fp)

    def query(
            self,
            name: str,
            job: str = None,
    ) -> List[dict]:
        name = name.lower()
        cond = pl.col('name').str.contains(name) | pl.col(
            'name2'
        ).str.to_lowercase().str.contains(name)

        if job is not None:
            cond = cond & (pl.col('job') == job)

        return self.df.filter(cond).select('*').to_dicts()

    def query_by_id(self, id_: int) -> dict:
        return self.df.filter(pl.col('id') == id_).limit(1).to_dicts()[0]


def get_magic_seal_repo():
    fp = config.get_magic_seal_parquet_file_path()
    return SkillRepo(fp)
