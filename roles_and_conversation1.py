import os

from autogen import ConversableAgent





agent = ConversableAgent(
    "chatbot",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("my_api_key")}]},
    code_execution_config=False,    # Turn off code execution, by default it is off.
    function_map=None,             # No registered functions, by default it is None.
    human_input_mode="NEVER",       # Never ask for human input.
)
reply = agent.generate_reply(messages=[{"content": "Tell me a joke.", "role": "user"}])  #indicate that the speaker is the user and message is user message
print(reply)


