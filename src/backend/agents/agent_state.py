from dataclasses import dataclass
from typing import TypedDict

from src.backend.models.miro_board import MiroBoard
from src.backend.enums.next_action import NextAction


@dataclass
class AgentState(TypedDict, total=False):
    next_action: NextAction
    current_board: MiroBoard
    new_board: MiroBoard

    def __init__(self):
        self.next_action = NextAction.NO_ACTION
        self.current_board = None
        self.new_board = None

