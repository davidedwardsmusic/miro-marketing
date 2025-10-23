import os
import time
from http.client import HTTPException

from dotenv import load_dotenv

from .agents.agent_state import AgentState
from .agents.plan_builder_agent import PlanBuilderAgent
from .manager.board_manager import BoardManager
from .miro_api import MiroApiClient
from .models.miro_board import MiroBoard
from src.backend.enums.next_action import NextAction


class BoardPoller:
    def __init__(self) -> None:
        load_dotenv()
        self.board_id = os.environ.get("MIRO_BOARD_ID")
        self.interval_seconds = int(os.environ.get("INTERVAL_SECONDS", "5"))
        self.miro_api_token = os.environ.get("MIRO_API_TOKEN")
        # Initialize API client
        self.api = MiroApiClient()
        # check-point the miro board
        self.current_board = self.api.load_board()
        self.manager = BoardManager(board=self.current_board)
        self.plan_builder_agent = PlanBuilderAgent()

    def poll_once(self) -> bool:
        """Perform a single poll cycle. Returns True if a change was detected and handled."""
        state: AgentState = \
            self.plan_builder_agent.invoke(self.current_board, self.api.load_board())
        action: NextAction = state.get("next_action")
        self.current_board = state.get("current_board")
        return action != NextAction.NO_ACTION

    def run_forever(self) -> None:
        print(f"[poller] Starting poller for board {self.board_id} every {self.interval_seconds}s")
        while True:
            try:
                changed = self.poll_once()
                print(f"[poller] cycle done: changed={changed}")
            except Exception as e:  # noqa: BLE001
                print(f"[poller] unexpected error: {e}")
            time.sleep(self.interval_seconds)

