from PySide6.QtCore import QObject, Signal


class GlobalSignals(QObject):
    pvf_changed = Signal()

    def __init__(self):
        super().__init__()


gs = GlobalSignals()

import enum

from PySide6.QtCore import QObject, Signal


class SubmitType(enum.Enum):
    Item = (1,)
    Equipment = (2,)


class SubmitSignal(QObject):
    on_submit = Signal(SubmitType, int)

    def __init__(self):
        super().__init__()
