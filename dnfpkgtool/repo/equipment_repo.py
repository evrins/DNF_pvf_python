from pathlib import Path
from typing import List

import polars as pl
from loguru import logger

from dnfpkgtool.pvf.pvf_reader import PVFDict, PVFReader
from dnfpkgtool.repo import remapping_pvf_dict, MappingElementLocation
from util import time_it


def map_armor_type(d: dict[str, str]) -> str:
    et = d["equipment_type"]
    ign = d["item_group_name"]
    if not ign:
        return ""
    if et in ["[coat]", "[waist]", "[shoulder]", "[pants]", "[shoes]"]:
        parts = ign.split(" ")
        if len(parts) != 2:
            raise ValueError("invalid item group name")
        return parts[0]
    return ""


equipment_mapping = {
    "": "契约效果",
    "[artifact blue]": "蓝色 宠物装备",
    "[artifact green]": "绿色 宠物装备",
    "[artifact red]": "红色 宠物装备",
    "[aurora avatar]": "光环",
    "[hair avatar]": "头部装扮",
    "[hat avatar]": "帽子装扮",
    "[face avatar]": "脸部装扮",
    "[breast avatar]": "胸部装扮",
    "[coat avatar]": "上衣装扮",
    "[skin avatar]": "皮肤装扮",
    "[waist avatar]": "腰部装扮",
    "[pants avatar]": "下装装扮",
    "[shoes avatar]": "脚部装扮",
    "[coat]": "上衣",
    "[waist]": "腰带",
    "[pants]": "下装",
    "[shoulder]": "头肩",
    "[shoes]": "鞋子",
    "[magic stone]": "魔法石",
    "[support]": "辅助装备",
    "[creature]": "宠物",
    "[title name]": "称号",
    "[weapon]": "武器",
    "[wrist]": "手镯",
    "[amulet]": "项链",
    "[ring]": "戒指",
}


def map_equipment_type_display(equipment_type: str) -> str:
    return equipment_mapping[equipment_type]


def map_rarity_display(d: dict[str, str | int]) -> str:
    id_ = d["id"]
    name = d["name"]
    rarity = d["rarity"]
    item_category = d["item_category"]

    name = name.strip()
    if name.startswith("传承"):
        return "传承"

    item_category = item_category.strip()
    if item_category == "boss drop":
        return "领主神器"

    if rarity == 0:
        return "普通"
    elif rarity == 1:
        return "高级"
    elif rarity == 2:
        return "稀有"
    elif rarity == 3:
        return "神器"
    elif rarity == 4:
        return "史诗"
    elif rarity == 5:
        return "勇者"

    raise ValueError(f"{id_} unknown rarity {rarity}")


def build_equipment_repo_parquet(pvf_dict: PVFDict, fp: str):
    mappings = [
        ("level", "[minimum level]", 0, MappingElementLocation.First),
        ("rarity", "[rarity]", 0, MappingElementLocation.First),
        ("equipment_type", "[equipment type]", "", MappingElementLocation.First),
        ("sub_equipment_type", "[equipment type]", 0, MappingElementLocation.Second),
        ("item_group_name", "[item group name]", "", MappingElementLocation.First),
        ("item_category", "[item category]", "", MappingElementLocation.First),
        ("usable_job", "[usable job]", [], MappingElementLocation.All),
    ]
    df = remapping_pvf_dict(pvf_dict, mappings)
    df = pl.DataFrame(df)
    df = df.with_columns(
        pl.struct(["id", "equipment_type", "item_group_name"])
        .map_elements(map_armor_type, return_dtype=pl.String)
        .alias("armor_type"),
        pl.col("equipment_type")
        .map_elements(map_equipment_type_display)
        .alias("equipment_type_display"),
        pl.struct(["id", "name", "rarity", "item_category"])
        .map_elements(map_rarity_display, return_dtype=pl.String)
        .alias("rarity_display"),
    )

    df = df.drop(["rarity", "item_category"])
    df.write_parquet(fp)


base_dir = Path(__file__).parent


def test_build_equipment_repo():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    stackable_dict = reader.get_equipment_dict()
    build_equipment_repo_parquet(
        stackable_dict, base_dir / "data" / "equipments.parquet"
    )


def test_query():
    fp = base_dir / "data" / "equipments.parquet"
    item_repo = EquipmentRepo(str(fp))
    res = item_repo.query("", ["[coat]", "[shoes]"], 1, 20, 1)
    print()
    print(f"{len(res)} equipments found")
    for it in res:
        print(it)


class EquipmentIdNotFoundException(Exception):
    def __init__(self, ep_id):
        self.ep_id = ep_id

        super().__init__("Equipment ID not found")

    def __str__(self):
        return f"Equipment ID not found: {self.ep_id}"


class EquipmentRepo:
    def __init__(self, fp: str):
        self.df = pl.read_parquet(fp)

    @time_it
    def query(
        self,
        name: str,
        equipment_type_list: List[str] = None,
        usable_job: str = None,
        item_group_name: str = None,
        armor_type: str = None,
        min_level: int = None,
        max_level: int = None,
        rarity: str = None,
        limit: int = None,
    ):
        logger.info(
            f"querying {name} equipment types {equipment_type_list} usable job {usable_job} item group {item_group_name} armor_type {armor_type} min_level {min_level} max_level {max_level} rarity {rarity}"
        )

        name = name.lower()
        cond = (pl.col("name").str.contains(name)) | (
            pl.col("name2").str.to_lowercase().str.contains(name)
        )

        if min_level is not None:
            cond = cond & (pl.col("level") >= min_level)
        if max_level is not None:
            cond = cond & (pl.col("level") <= max_level)

        if rarity is not None:
            cond = cond & (pl.col("rarity_display") == rarity)

        if equipment_type_list is not None:
            cond = cond & (pl.col("equipment_type").is_in(equipment_type_list))

        if usable_job is not None:
            cond = cond & (pl.col("usable_job").list.contains(usable_job))

        if item_group_name is not None:
            cond = cond & (pl.col("item_group_name") == item_group_name)

        if armor_type is not None:
            cond = cond & (pl.col("armor_type") == armor_type)

        query = self.df.filter(cond)
        if limit is not None:
            query = query.limit(limit)
        rs = query.to_dicts()
        logger.info(f"found {len(rs)} equipments found")
        return rs

    def query_by_id(self, id_: int) -> dict:
        rows = self.df.filter(pl.col("id") == id_).head(1).to_dicts()
        if len(rows) == 0:
            raise EquipmentIdNotFoundException(id_)
        return rows[0]
