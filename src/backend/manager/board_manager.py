from src.backend.agents.plan_builder_agent import PlanBuilderAgent
from src.backend.miro_api import MiroApiClient
from src.backend.models.miro_board import MiroBoard


class BoardManager:
    def __init__(self, board: MiroBoard):
        self.board = board
        self.api = MiroApiClient()
        self.agent = PlanBuilderAgent()

