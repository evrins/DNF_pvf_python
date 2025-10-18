import threading
import uuid


def gen_mac_address() -> str:
    mac_address = uuid.uuid1().hex[-12:].upper()
    mac_address = '-'.join([mac_address[i : i + 2] for i in range(0, 11, 2)])
    return mac_address


def in_thread(func):
    def inner(*args, **kw):
        t = threading.Thread(target=lambda: func(*args, **kw))
        t.daemon = True
        t.start()
        return t

    return inner


def decrypt_bytes(input_bytes: bytes, crc):
    """对原始字节流进行初步预处理"""
    key = 0x81A79011
    xor = crc ^ key
    int_num = len(input_bytes) // 4
    key_all = xor.to_bytes(4, 'little') * int_num
    value_xored_all = int.from_bytes(key_all, 'little') ^ int.from_bytes(
        input_bytes, 'little'
    )
    mask_1 = 0b00000000_00000000_00000000_00111111
    mask_2 = 0b11111111_11111111_11111111_11000000
    mask_1_all = int.from_bytes(mask_1.to_bytes(4, 'little') * int_num, 'little')
    mask_2_all = int.from_bytes(mask_2.to_bytes(4, 'little') * int_num, 'little')
    value_1 = value_xored_all & mask_1_all
    value_2 = value_xored_all & mask_2_all
    value = value_1 << 26 | value_2 >> 6
    return value.to_bytes(4 * int_num, 'little')
