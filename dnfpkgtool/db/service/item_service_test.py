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
        for it in item.display_magic_seals:
            if it.id == 0:
                continue
            print(f'{it.id} {it.name} {it.level} {(it.level + offset) % 8}')
        print('-' * 8)
    print(item)

def test_unpack_blob_item_2():
    buf = b'\x00\x01i\xca\x06\x00\x0f\xeb~\xcd\x0b\x00\x00\xb9\xb4\x98\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    svc = ItemService()
    item = svc.unpack_blob_item(buf)
    print(item)

def test_get_current_character_cargo():
    svc = ItemService()
    items = svc.get_current_character_cargo()
    for it in items:
        print(f'{it}')


def test_get_current_character_inventory():
    svc = ItemService()
    ci = svc.get_current_character_inventory()
    print('equipments:')
    for it in ci.equipments:
        print(f'{it}')

    print('creatures:')
    for it in ci.creatures:
        print(f'{it}')

    print('backpack:')
    for it in ci.backpack:
        print(f'{it}')
