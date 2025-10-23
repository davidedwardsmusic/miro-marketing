from langgraph.graph import StateGraph, START, END

from src.backend.agents.agent_state import AgentState
from src.backend.agents.action_chooser import ActionChooser
from src.backend.agents.plan_refresher import PlanRefresher
from src.backend.agents.segment_predictor import SegmentPredictor
from src.backend.boarditems.chat_frame import ChatFrame
from src.backend.boarditems.frame_definitions import FrameDefinitions
from src.backend.enums.next_action import NextAction
from src.backend.miro_api import MiroApiClient
from src.backend.models.miro_board import MiroBoard


class PlanBuilderAgent:
    def __init__(self):
        self.agent = self._build_agent()

    def invoke(self, current_board: MiroBoard, new_board: MiroBoard) -> AgentState:
        final_state = self.agent.invoke( \
            AgentState(current_board=current_board, new_board=new_board))
        return final_state

    def add_initial_chat_frame(self, state: AgentState):
        """
        This is an agent node that adds the initial chat frame to the board.
        :param state:
        :return:
        """
        # validate that the next_action is ADD_INITIAL_CHAT_FRAME
        next_action = state.get("next_action")
        if next_action != NextAction.ADD_INITIAL_CHAT_FRAME:
            raise Exception(f"Invalid next_action: {next_action.value}. Should be ADD_INITIAL_CHAT_FRAME")

        print(f"[add_initial_chat_frame] next: {state.get('next_action')}")
        # add the initial chat frame
        frame=FrameDefinitions().chat
        chat_frame = ChatFrame(frame=frame, agent_content="Would you like me to set up your marketing board?")
        chat_frame.push_to_miro()
        return {}

    def choose_next_action(self, state: AgentState):
        print(f"[choose_next_action] next: {state.get('next_action')}")
        return ActionChooser().choose_next_action(state)

    def predict_segments(self, state: AgentState):
        print(f"[predict_segments] next: {state.get('next_action')}")
        return SegmentPredictor().predict_segments(state)

    def predict_channels(self, state: AgentState):
        print("[predict_channels] Predicting channels")
        return {}

    def refresh_plan(self, state: AgentState):
        print("[refresh_plan] Refreshing plan")
        return PlanRefresher().refresh_plan(state)

    def set_up_board(self, state: AgentState):
        """
        This is an agent node that sets up the board.
        :param state:
        :return:
        """
        already_set_up = state.get('new_board').is_set_up()
        if already_set_up:
            print("[set_up_board] Board already set up. Skipping.")
            return {}

        print("[set_up_board] Setting up")
        frame_defs = FrameDefinitions()
        frame_defs.product.push_to_miro()
        frame_defs.segments.push_to_miro()
        frame_defs.channels.push_to_miro()
        frame_defs.summary.push_to_miro()

        api = MiroApiClient()
        fresh_board: MiroBoard = api.load_board()
        fresh_board.add_sticky_note('Product', "Product Name: ", 200, 500)
        fresh_board.add_sticky_note('Product', "Product Description: ", 500, 500)
        fresh_board.add_sticky_note('Product', "What problem does it solve? ", 200, 800)
        fresh_board.add_sticky_note('Product', "Unique Value Proposition: ", 500, 800)
        fresh_board.add_sticky_note('Product', "Goals: ", 200, 1100)

        fresh_board.set_agent_prompt('Segments Chat', 'Agent: Would you like me to suggest some segments based on your product specifications?')
        fresh_board.set_agent_prompt('Channels Chat', 'Agent: Would you like me to suggest some channels based on your segments?')
        fresh_board.set_agent_prompt('Summary Chat', 'Agent: Would you like me to refresh your marketing plan?')
        return {}

    def route_after_choose(self, state: AgentState):
        next_action = state.get("next_action")
        print(f"[route_after_choose] Next action: {next_action}")

        # If next_action is None or NO_ACTION, go to END
        if next_action is None or next_action == NextAction.NO_ACTION:
            return END

        # Convert enum name to lowercase node name (e.g., ADD_INITIAL_CHAT_FRAME -> add_initial_chat_frame)
        return next_action.name.lower()

    def _build_agent(self):
        g = StateGraph(AgentState)

        # Nodes
        g.add_node("choose_next_action", self.choose_next_action)
        g.add_node("add_initial_chat_frame", self.add_initial_chat_frame)
        g.add_node("set_up_board", self.set_up_board)
        g.add_node("predict_segments", self.predict_segments)
        g.add_node("predict_channels", self.predict_channels)
        g.add_node("refresh_plan", self.refresh_plan)

        # Edges
        g.add_edge(START, "choose_next_action")
        g.add_conditional_edges("choose_next_action", self.route_after_choose)
        g.add_edge("add_initial_chat_frame", END)
        g.add_edge("set_up_board", END)
        g.add_edge("predict_segments", END)
        g.add_edge("predict_channels", END)
        g.add_edge("refresh_plan", END)

        return g.compile()

