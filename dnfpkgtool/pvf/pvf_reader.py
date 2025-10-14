import re
import struct
import traceback
from dataclasses import dataclass, field
from typing import List, Dict

from cachetools import cached
from loguru import logger

from dnfpkgtool.pvf.cache import lru_cache
from dnfpkgtool.pvf.lst import Lst
from dnfpkgtool.pvf.pvf_header import parse_pvf_header, PVFHeader
from dnfpkgtool.pvf.str import Str
from dnfpkgtool.pvf.string_table import StringTable
from dnfpkgtool.utils import decrypt_bytes

type PVFDict = dict[str, dict[str, List[str | int | float]]]


@dataclass
class BinaryContent:
    types: List[int] = field(default_factory=list)
    values: List[int | str | float] = field(default_factory=list)


class PVFReader:
    header: PVFHeader | None = None

    def __init__(self, filename: str, encode="big5"):
        super().__init__()
        self.filename = filename
        self.encode = encode

        self.f = open(filename, "rb")

        self.header = parse_pvf_header(self.f)

        string_table_bytes = self.read_file("stringtable.bin")
        self.string_table = StringTable(string_table_bytes, self.encode)

        self.n_string_lst = self.load_lst_file("n_string.lst")

    def close(self):
        self.f.close()
        lru_cache.clear()

    @cached(cache=lru_cache)
    def read_file(self, file_key: str) -> bytes:
        file_key = file_key.replace("//", "/").replace("\\", "/").lower()
        leaf_node = self.header.leaf_dict.get(file_key, None)
        if leaf_node is None:
            raise ValueError(f"File {file_key} not found")

        self.f.seek(self.header.file_pack_index_shift + leaf_node.relative_offset)
        buf = self.f.read(leaf_node.file_length)
        res = decrypt_bytes(buf, leaf_node.file_crc32)
        return res

    @cached(cache=lru_cache)
    def load_lst_file(self, path="", encode=""):
        content = self.read_file(path)
        if encode == "":
            encode = self.encode
        if "/" in path:
            base_dir, _ = path.rsplit("/", 1)
        else:
            base_dir = ""
        return Lst(content, self.string_table, base_dir=base_dir, encode=encode)

    @cached(cache=lru_cache)
    def read_n_from_lst_file(self, lst_file: Lst, idx: int) -> Str:
        file_key = lst_file[idx]
        content = self.read_file(file_key)
        return Str(content.decode(self.encode, "ignore"))

    @cached(cache=lru_cache)
    def read_file_as_dict(self, fpath: str) -> dict[str, List[str | int]]:
        res = self.read_file_as_list(fpath)
        key_count: dict[str, int] = {}
        values: List[str | int | float] = []
        current_key: str = ""

        d = {}

        n = len(res.types)
        for i in range(n):
            # segment start or close
            if res.types[i] == 5:
                # current_key is not set, set key and continue
                if current_key == "":
                    current_key = res.values[i]
                    continue
                # close segment skip
                if res.values[i].startswith("[/"):
                    continue
                count = key_count.get(current_key, 0)
                key_count[current_key] = count + 1
                if count > 0:
                    current_key = f"{current_key}-{count}"
                d[current_key] = values
                # set new segment key
                current_key = res.values[i]
                # empty values
                values = []
            else:
                values.append(res.values[i])

        # set last
        count = key_count.get(current_key, 0)
        if count > 0:
            current_key = f"{current_key}-{count}"
        d[current_key] = values

        return d

    @cached(cache=lru_cache)
    def read_file_as_list(self, fpath: str, string_quote: str = "") -> BinaryContent:
        content = self.read_file(fpath)
        return self.content_2_list(content, string_quote)

    @cached(cache=lru_cache)
    def content_2_list(self, content: bytes, string_quote="") -> BinaryContent:
        """读取二进制文本，如stk文件，将解密字段类型和关键字返回为list"""
        res = BinaryContent()
        if not content:
            return res

        shift = 2
        unit_num = (len(content) - 2) // 5

        struct_pattern = "<"
        unit_types = []
        for i in range(unit_num):
            unit_type = content[shift + i * 5]
            unit_types.append(unit_type)
            if unit_type == 4:
                struct_pattern += "Bf"
            else:
                struct_pattern += "Bi"

        units = struct.unpack(struct_pattern, content[2 : 2 + 5 * unit_num])
        types = units[::2]
        values = units[1::2]

        for i in range(unit_num):
            if types[i] in [2, 3, 4]:
                res.values.append(values[i])
            elif types[i] in [5, 6, 8]:
                res.values.append(self.string_table[values[i]])
            elif types[i] == 7:
                res.values.append(
                    string_quote + self.string_table[values[i]] + string_quote
                )
            elif types[i] == 9:
                string_key = self.string_table[values[i + 1]]
                string_dict = self.read_n_from_lst_file(self.n_string_lst, values[i])
                res.values.append(string_dict[string_key])
            else:
                continue
            res.types.append(types[i])

        return res

    @cached(cache=lru_cache)
    def get_magic_seal_dict(self) -> dict[int, str]:
        logger.info("loading magic seal ...")
        magic_seal_path = "etc/randomoption/randomizedoptionoverall2.etc"
        res = self.read_file_as_list(magic_seal_path)

        n = len(res.types)

        magic_seal_dict = {}

        for i in range(2, n):
            if res.values[i] == "[/postfix]":
                # end of parse
                break
            if res.types[i] == 2:
                magic_seal_dict[res.values[i]] = self._extract_magic_seal(
                    res.values[i + 1]
                )

        return magic_seal_dict

    def _extract_magic_seal(self, magic_seal: str) -> str:
        pattern = r"[\u4e00-\u9fff]+"
        res = re.findall(pattern, magic_seal)
        return res[0]

    def get_skill_list(self) -> List[Dict[str, any]]:
        skill_list_path = "skill/skilllist.lst"
        skill_lst = self.load_lst_file(skill_list_path)
        skills = []
        # list all job skill
        for k, v in skill_lst.table_dict.items():
            # list single job skill
            job_skill_list = self.load_lst_file(f"{skill_lst.base_dir}/{v}")
            for k1, v1 in job_skill_list.table_dict.items():
                job_name = v1.split("/")[0]
                job_skill_dict = self.read_file_as_dict(f"{skill_lst.base_dir}/{v1}")
                job_skill_dict["job"] = [job_name.lower()]
                skills.append(job_skill_dict)
        return skills

    def get_avatar_hidden_fixed(self) -> PVFDict:
        avatar_hidden_path = "etc/avatar_roulette/avatarfixedhiddenoptionlist.etc"
        avatar_lst = self.read_file_as_list(avatar_hidden_path)
        print(avatar_lst)
        return None

    def get_equipment_dict(self) -> PVFDict:
        return self.get_as_dict("equipment/equipment.lst", "Equipment")

    def get_stackable_dict(self) -> PVFDict:
        return self.get_as_dict("stackable/stackable.lst", "Item")

    def get_exp_table(self) -> List[int]:
        exp_table_path = "character/exptable.tbl"
        exp_table_list = self.read_file_as_list(exp_table_path)
        return exp_table_list.values

    def get_job_dict(self) -> tuple[dict, PVFDict]:
        job_dict = {}
        jog_tag_dict = {}

        logger.info("loading job info ...")

        characters = self.load_lst_file("character/character.lst")

        for id_, path_ in characters.table_dict.items():
            character = self.read_file_as_dict(characters.base_dir + "/" + path_)
            job_dict[id_] = dict(enumerate(character["[growtype name]"]))
            jog_tag_dict[id_] = character["[job]"][0]

        return job_dict, jog_tag_dict

    def get_quest_dict(self) -> PVFDict:
        return self.get_as_dict("n_quest/quest.lst", "quest")

    def get_dungeon_dict(self) -> PVFDict:
        return self.get_as_dict("dungeon/dungeon.lst", "dungeon")

    @cached(cache=lru_cache)
    def get_as_dict(self, lst_file_name: str, dict_name: str) -> PVFDict:
        lst_file = self.load_lst_file(lst_file_name)

        logger.info(f"loading {dict_name} list...({len(lst_file)})")

        res = {}
        duplicated = []
        failure = []

        for id_, path_ in lst_file.table_dict.items():
            if id_ in res:
                duplicated.append(id_)

            try:
                fpath = lst_file.base_dir + "/" + path_
                fpath = fpath.replace("//", "/")
                res[id_] = self.read_file_as_dict(fpath)
            except Exception as e:
                traceback.print_exc()
                logger.error(f"failed to read file {id_} {path_}: {e}")
                failure.append((id_, path_))

        if duplicated:
            logger.warning(f"duplicated {dict_name} list: {len(duplicated)}")

        if failure:
            logger.warning(f"failure {dict_name} list: {len(failure)}")

        return res
