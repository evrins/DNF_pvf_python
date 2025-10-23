from dnfpkgtool.db.repo.account_cargo_repo import AccountCargoRepo
from dnfpkgtool.db.service.item_service import ItemService


def test_unpack_blob_items():
    repo = AccountCargoRepo()
    account_cargo = repo.query_by_m_id(18000000)
    svc = ItemService()
    items = svc.unpack_blob_items(account_cargo.cargo)
    for it in items:
        print(f'{it}')


def test_unpack_blob_item():
    buf = bytes.fromhex(
        '010180a7220001236a00001b000000000000000000000000000000000000000000000000008e000a020014f4001e91c100280000000000000000000000'
    )
    svc = ItemService()
    item = svc.unpack_blob_item(buf)
    print(item)


def test_unpack_blob_item_1():
    buf = bytes.fromhex(
        '010183242300001869fc2d28000000000000000000c30b0000c6d9e068c402000000000000580b184c12175a10157a0000000000000000000000000000'
    )
    svc = ItemService()
    item = svc.unpack_blob_item(buf)
    for offset in range(1, 8):
        for it in item.display_seals:
            if it.id == 0:
                continue
            print(f'{it.id} {it.name} {it.level} {(it.level + offset) % 8}')
        print('-' * 8)
    print(item)
