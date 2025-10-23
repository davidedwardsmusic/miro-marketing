from dataclasses import dataclass
from enum import Enum, auto


class NextAction(Enum):
    CHOOSE_NEXT_ACTION = auto()
    ADD_INITIAL_CHAT_FRAME = auto()
    SET_UP_BOARD = auto()
    PREDICT_SEGMENTS = auto()
    PREDICT_CHANNELS = auto()
    REFRESH_PLAN = auto()
    NO_ACTION = auto()
