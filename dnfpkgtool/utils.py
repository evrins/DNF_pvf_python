import threading
import uuid


def gen_mac_address() -> str:
    mac_address = uuid.uuid1().hex[-12:].upper()
    mac_address = "-".join([mac_address[i: i + 2] for i in range(0, 11, 2)])
    return mac_address


def in_thread(func):
    def inner(*args, **kw):
        t = threading.Thread(target=lambda: func(*args, **kw))
        t.daemon = True
        t.start()
        return t

    return inner
