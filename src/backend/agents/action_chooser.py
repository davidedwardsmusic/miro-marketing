import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.backend.agents.agent_node import AgentNode
from src.backend.agents.agent_state import AgentState
from src.backend.models.miro_board import MiroBoard
from src.backend.enums.next_action import NextAction
from dataclasses import replace


def _load_prompt_template(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompts_dir = Path(__file__).parent / "prompts"
    prompt_file = prompts_dir / filename
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()



class ActionChooser(AgentNode):
    def __init__(self):
        super().__init__(NextAction.CHOOSE_NEXT_ACTION.name)

    def choose_next_action(self, state: AgentState):
        """
        This is an agent node that chooses the next action to take.
        To do that, it:
        1. Checks to see if the board has changed.
           If not, it returns NO_ACTION
           elif the board is empty, it returns ADD_INITIAL_CHAT_FRAME
           elif asks the llm to compare the current and new board and determine the next action
        :param state:
        :return:
        """
        current = state.get("current_board")
        new: MiroBoard = state.get("new_board")

        # Nothing on the board yet
        if new.is_empty():
            next_action = NextAction.ADD_INITIAL_CHAT_FRAME
            return {"current_board": replace(new),
                    "next_action": next_action}

        # Board has not changed
        elif current == new:
            return {"current_board": replace(new),
                    "next_action": NextAction.NO_ACTION}

        # Need to do LLM analysis here
        else:
            next_action = self.ask_llm_for_next_action(current, new)
            new.clear_user_responses()
            return {"current_board": replace(new),
                    "next_action": next_action}


    def ask_llm_for_next_action(self, current: MiroBoard, new: MiroBoard) -> NextAction:
        """
        Uses GPT-4 to analyze the current and new board states and determine the next action.
        Currently checks if the user answered affirmatively to "Would you like me to set up your marketing board?"

        Args:
            current: The previous board state
            new: The new board state

        Returns:
            NextAction enum indicating what action should be taken
            :type current: object
        """
        load_dotenv()

        # Initialize the LLM
        model_name = os.getenv("OPENAI_MODEL", "gpt-5")
        llm = ChatOpenAI(model=model_name, temperature=0)

        board_json = new.to_json_for_llm()

        # Load prompts from files
        system_prompt_text = _load_prompt_template("choose_next_action_system.txt")
        user_prompt_template = _load_prompt_template("choose_next_action_user.txt")

        # Format the user prompt with board states
        user_prompt_text = user_prompt_template.format(board_state=board_json)

        # Create the messages
        system_prompt = SystemMessage(content=system_prompt_text)
        human_prompt = HumanMessage(content=user_prompt_text)

        # Get LLM response
        response = llm.invoke([system_prompt, human_prompt])
        response_text = response.content.strip().upper()

        next_action = NextAction[response_text]
        return next_action
