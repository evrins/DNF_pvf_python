import json
import os
from pathlib import Path

from dnfpkgtool.pvf.pvf_reader import PVFReader

base_dir = Path(__file__).parent / "dump"

os.makedirs(base_dir, exist_ok=True)


def save_obj_2_file(obj, filename):
    with open(base_dir / filename, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)


def test_pvf_reader():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    st = reader.string_table

    all_strings = []
    for i in range(2 * st.length):
        all_strings.append(st[i])

    all_strings.sort()
    with open(base_dir / "string_table.txt", "w") as f:
        f.writelines(all_strings)


def test_get_quest_dict():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    quest_dict = reader.get_quest_dict()
    save_obj_2_file(quest_dict, "quest_dict.json")


def test_get_dungeon_dict():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    dungeon_dict = reader.get_dungeon_dict()
    save_obj_2_file(dungeon_dict, "dungeon_dict.json")


def test_get_magic_seal_dict():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    magic_seal_dict = reader.get_magic_seal_dict()
    save_obj_2_file(magic_seal_dict, "magic_seal_dict.json")


def test_get_job_dict():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    job_dict = reader.get_job_dict()
    save_obj_2_file(job_dict, "job_dict.json")


def test_get_exp_table():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    exp_table = reader.get_exp_table()
    save_obj_2_file(exp_table, "exp_table.json")


def test_get_stackable_dict():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    stackable_dict = reader.get_stackable_dict()
    save_obj_2_file(stackable_dict, "stackable_dict.json")


def test_get_avatar_hidden_fixed():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    avatar_hidden_dict = reader.get_avatar_hidden_fixed()
    save_obj_2_file(avatar_hidden_dict, "stackable_dict.json")


def test_get_equipment():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    equipment_dict = reader.get_equipment_dict()
    save_obj_2_file(equipment_dict, "equipment_dict.json")


def test_get_skill_list():
    pvf_path = "/Users/evrins/workspace/python/DNF_pvf_python/Script.pvf"
    reader = PVFReader(pvf_path)
    skill_dict = reader.get_skill_list()
    save_obj_2_file(skill_dict, "skill_list.json")
