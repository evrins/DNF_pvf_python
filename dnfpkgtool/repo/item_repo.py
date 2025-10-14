from pathlib import Path
from typing import List

import polars as pl
from loguru import logger

from dnfpkgtool.pvf.pvf_reader import PVFDict, PVFReader
from dnfpkgtool.repo import MappingElementLocation, remapping_pvf_dict
from ui.vars import item_rarity_list

stackable_mapping = {
    "[avatar emblem]": "时装徽章",
    "[booster random]": "礼包",
    "[booster selection]": "礼包",
    "[booster]": "礼包",
    "[cera booster]": "礼包",
    "[cera package]": "礼包",
    "[usable cera package]": "礼包",
    "[upgrade limit cube]": "礼包",
    "[contract]": "契约",
    "[creature expitem]": "宠物道具",
    "[creature]": "宠物道具",
    "[feed]": "宠物道具",
    "[disguise random]": "变身道具",
    "[disguise]": "变身道具",
    "[dye]": "染色剂",
    "[enchant waste]": "附魔宝珠",
    "[expert town potion]": "秘药",
    "[global effect]": "频道道具",
    "[material expert job]": "副职业",
    "[material]": "材料",
    "[etc]": "其他",
    "[legacy]": "其他",
    "[multi upgradable legacy bonus cera]": "其他",
    "[multi upgradable legacy]": "其他",
    "[stackable legacy]": "其他",
    "[only effect]": "其他",
    "[town and dungeon]": "其他",
    "[unlimited town and dungeon]": "其他",
    "[unlimited etc]": "其他",
    "[upgradable legacy]": "袖珍罐",
    "[quest receive]": "悬赏令",
    "[quest]": "任务道具",
    "[recipe]": "设计图",
    "[set]": "地雷",
    "[teleport potion]": "瞬间移动药剂",
    "[throw]": "投掷物",
    "[waste]": "消耗品",
    "[unlimited waste]": "消耗品",
}


def map_stackable_type(d: dict[str, str]) -> str:
    item_category = d["item_category"]
    if item_category == "monster card":
        return "卡片"
    stackable_type = d["stackable_type"]
    return stackable_mapping[stackable_type]


def map_rarity_display(rarity: int) -> str:
    rarity_display = item_rarity_list[rarity]
    return rarity_display


def build_item_repo_parquet(pvf_dict: PVFDict, fp: str):
    mappings = [
        ("level", "[minimum level]", 0, MappingElementLocation.First),
        ("rarity", "[rarity]", 0, MappingElementLocation.First),
        ("stackable_type", "[stackable type]", "", MappingElementLocation.First),
        ("sub_stackable_type", "[stackable type]", 0, MappingElementLocation.Second),
        ("item_group_name", "[item group name]", "", MappingElementLocation.First),
        ("item_category", "[item category]", "", MappingElementLocation.First),
    ]
    df = remapping_pvf_dict(pvf_dict, mappings)
    df = pl.DataFrame(df)
    df = df.with_columns(
        pl.struct(["stackable_type", "item_category"])
        .map_elements(map_stackable_type, return_dtype=pl.String)
        .alias("stackable_type_display"),
        pl.col("rarity")
        .map_elements(map_rarity_display, return_dtype=pl.String)
        .alias("rarity_display"),
    )
    df.write_parquet(fp)


base_dir = Path(__file__).parent


def test_build_item_repo_parquet():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    stackable_dict = reader.get_stackable_dict()
    build_item_repo_parquet(stackable_dict, base_dir / "data" / "items.parquet")


def test_query():
    fp = base_dir / "data" / "items.parquet"
    item_repo = ItemRepo(str(fp))
    rs = item_repo.query("药", max_level=50)
    print(len(rs))


def test_query_by_id():
    fp = base_dir / "data" / "items.parquet"
    item_repo = ItemRepo(str(fp))
    res = item_repo.query_by_id(1)
    print()
    print(res)


class ItemIdNotFoundException(Exception):
    def __init__(self, item_id):
        self.item_id = item_id
        super().__init__("Item ID not found")

    def __str__(self):
        return f"Item ID not found: {self.item_id}"


class ItemRepo:
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
