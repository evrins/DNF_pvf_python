from pathlib import Path
from typing import List, Dict

import polars as pl
from loguru import logger

from dnfpkgtool.pvf.pvf_reader import PVFReader
from dnfpkgtool.repo import MappingElementLocation, remapping_pvf_list


def build_skill_repo_parquet(pvf_list: List[Dict[str, any]], fp: str):
    mappings = [
        ("job", "job", 0, MappingElementLocation.First),
        ("name", "[name]", "", MappingElementLocation.First),
        ("name2", "[name2]", "", MappingElementLocation.First),
        ("basic_explain", "[basic explain]", "", MappingElementLocation.First),
        ("explain", "[explain]", "", MappingElementLocation.First),
        (
            "feature_skill_index",
            "[feature skill index]",
            0,
            MappingElementLocation.First,
        ),
        ("skill_class", "[skill class]", 0, MappingElementLocation.First),
    ]
    df = remapping_pvf_list(pvf_list, mappings)
    df = pl.DataFrame(df)

    df.write_parquet(fp)


base_dir = Path(__file__).parent


def test_build_skill_repo_parquet():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    stackable_dict = reader.get_skill_list()
    build_skill_repo_parquet(stackable_dict, base_dir / "data" / "skills.parquet")


def test_query():
    fp = base_dir / "data" / "items.parquet"
    skill_repo = SkillRepo(str(fp))
    rs = skill_repo.query("药", max_level=50)
    print(len(rs))


class ItemIdNotFoundException(Exception):
    def __init__(self, item_id):
        self.item_id = item_id
        super().__init__("Item ID not found")

    def __str__(self):
        return f"Item ID not found: {self.item_id}"


class SkillRepo:
    def __init__(self, fp: str):
        self.df = pl.read_parquet(fp)

    def query(
        self,
        name: str,
        stackable_type_list: list[str] = None,
        min_level: int = None,
        max_level: int = None,
        rarity_display: str = None,
        item_type: str = None,
    ) -> List[dict]:
        logger.info(
            f"query with name {name} stackable_type_list {stackable_type_list} min_level {min_level} max_level {max_level} rarity_display {rarity_display} item_type {item_type}"
        )
        name = name.lower()
        cond = pl.col("name").str.contains(name) | pl.col(
            "name2"
        ).str.to_lowercase().str.contains(name)

        if stackable_type_list is not None:
            cond = cond & (pl.col("stackable_type").is_in(stackable_type_list))
        if min_level is not None:
            cond = cond & (pl.col("level") >= min_level)
        if max_level is not None:
            cond = cond & (pl.col("level") <= max_level)
        if rarity_display is not None:
            cond = cond & (pl.col("rarity_display") == rarity_display)
        if item_type is not None:
            cond = cond & (pl.col("item_type") == item_type)

        return self.df.filter(cond).select("*").to_dicts()

    def query_by_id(self, id_: int) -> dict:
        rows = self.df.filter(pl.col("id") == id_).head(1).to_dicts()
        if len(rows) == 0:
            raise ItemIdNotFoundException(id_)
        return rows[0]
