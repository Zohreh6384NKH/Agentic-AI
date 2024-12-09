import autogen
from autogen import UserProxyAgent, AssistantAgent
from typing import Annotated
import os



# Create the User Proxy Agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
    max_consecutive_auto_reply=10,
    code_execution_config=False,
)

# Register function for execution
@user_proxy.register_for_execution()
def add_numbers(
    a: Annotated[int, "the first number"],
    b: Annotated[int, "the second number"]
) -> int:
    return a + b

# Create an Assistant Agent
assistant = AssistantAgent(
    name="assistant",
    system_message="You can ask me to add numbers. I will use a helper function to calculate the result.",
   llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    
    max_consecutive_auto_reply=2,
)

# Initiate chats
chat_results = user_proxy.initiate_chats(
    [
        {
            "recipient": assistant,
            "message": "add_numbers: {a: 5, b: 9}",
            "clear_history": True,
            "silent": False,
            "summary_method": "last_msg",
        }
    ]
)

