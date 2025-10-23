import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from src.backend.agents.agent_node import AgentNode
from src.backend.agents.agent_state import AgentState
from src.backend.enums.next_action import NextAction
from src.backend.miro_api import MiroApiClient
from src.backend.models.miro_board import MiroBoard
from src.backend.models.miro_item import MiroItem


def _load_prompt_template(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompts_dir = Path(__file__).parent / "prompts"
    prompt_file = prompts_dir / filename
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


class SegmentPredictor(AgentNode):
    def __init__(self):
        super().__init__(NextAction.PREDICT_SEGMENTS.name)
        self.segment_frame: MiroItem = None

    def _add_segment_sticky_internal(self, content: str):
        """Internal method to add a sticky note to the segment frame."""
        api = MiroApiClient()
        point = self.segment_frame.get_next_available_sticky_position()
        api.create_parented_sticky_note(self.segment_frame.id, content, point.x, point.y)

    def predict_segments(self, state: AgentState):
        board_state: MiroBoard = state.get("new_board")
        self.segment_frame = board_state.get_segment_frame()
        self.product_frame = board_state.get_product_frame()
        product_info = self.product_frame.dump_sticky_notes()

        # Define the tool that the LLM can call (as a closure to capture 'self')
        @tool
        def add_segment_sticky(segment_name: str, segment_description: str) -> str:
            """Add a customer segment sticky note to the Segments frame.

            Args:
                segment_name: The name of the customer segment (e.g., "Tech Enthusiasts")
                segment_description: A brief description of this segment and why they would be interested

            Returns:
                Confirmation message
            """
            # Format the content for the sticky note
            content = f"<p><strong>{segment_name}</strong></p><p>{segment_description}</p>"

            # Call the instance method to add the sticky (self is captured from outer scope)
            self._add_segment_sticky_internal(content)

            return f"Added segment: {segment_name}"

        # Initialize the LLM
        load_dotenv()
        model_name = os.getenv("OPENAI_MODEL", "gpt-5")
        llm = ChatOpenAI(model=model_name, temperature=0.7)

        # Bind the tool to the LLM
        llm_with_tools = llm.bind_tools([add_segment_sticky])

        # Load the system prompt
        system_prompt_text = _load_prompt_template("segment_predictor_system.txt")
        system_message = SystemMessage(content=system_prompt_text)

        # Create the user prompt with product info
        user_message = HumanMessage(content=f"Product Information:\n{product_info}\n\nIdentify customer segments for this product.")

        # Invoke the LLM
        messages = [system_message, user_message]
        response = llm_with_tools.invoke(messages)

        # Process tool calls in a loop until the LLM is done
        while response.tool_calls:
            # Add the AI response to messages
            messages.append(response)

            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(f"[segment_predictor] LLM calling tool: {tool_name} with args: {tool_args}")

                # Execute the tool
                if tool_name == "add_segment_sticky":
                    result = add_segment_sticky.invoke(tool_args)
                    print(f"[segment_predictor] Tool result: {result}")

                    # Add the tool result to messages
                    tool_message = ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"]
                    )
                    messages.append(tool_message)

            # Get the next response from the LLM
            response = llm_with_tools.invoke(messages)

        print(f"[segment_predictor] Segment prediction complete")
        return {}



