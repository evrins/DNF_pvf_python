import zlib
from typing import List, Tuple

from config import config
from dnfpkgtool.db.entity.dnf_item_slot import DnfItemSlot
from dnfpkgtool.db.entity.magic_seal import MagicSeal
from dnfpkgtool.db.repo.account_cargo_repo import get_account_cargo_repo
from dnfpkgtool.repo.equipment_repo import get_equipment_repo
from dnfpkgtool.repo.item_repo import get_item_repo
from dnfpkgtool.repo.magic_seal_repo import get_magic_seal_repo


class ItemService:
    def __init__(self):
        self.item_repo = get_item_repo()
        self.equipment_repo = get_equipment_repo()
        self.magic_seal_repo = get_magic_seal_repo()
        self.account_cargo_repo = get_account_cargo_repo()

    def get_current_account_cargo(self) -> List[DnfItemSlot]:
        account_id = config.get_current_account_id()
        account_cargo = self.account_cargo_repo.query_by_m_id(account_id)
        return self.unpack_blob_items(account_cargo.cargo)

    def unpack_blob_items(self, buf: bytes) -> List[DnfItemSlot]:
        buf = zlib.decompress(buf[4:])
        num = len(buf) // 61
        res = []
        for i in range(num):
            item = self.unpack_blob_item(buf[i * 61: (i + 1) * 61])
            item.display_idx = i
            res.append(item)
        return res

    def unpack_blob_item(self, buf: bytes) -> DnfItemSlot:
        item = DnfItemSlot(buf)
        if item.id:
            if item.type == 0x01:
                inner_item = self.equipment_repo.query_by_id(item.id)
            else:
                inner_item = self.item_repo.query_by_id(item.id)
            item.display_name = inner_item['name']
            item.display_rarity = inner_item['rarity']
            item.display_rarity_name = inner_item['rarity_display']

        magic_seal_range_list = [(0, 3), (3, 6), (6, 9), (10, 13)]
        for idx, it in enumerate(magic_seal_range_list):
            ms = MagicSeal.from_bytes(item.magic_seal[it[0]: it[1]])
            if ms.id == 0:
                continue
            ms.name = self.magic_seal_repo.query_by_id(ms.id)['name']
            item.display_seals[idx] = ms
        return item


def get_item_service() -> ItemService:
    return ItemService()
