import os
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

config_list = config_list_from_json(
    env_or_file = "OAI_CONFIG_LIST.json"
)
assistant = AssistantAgent(
    name="assistant",
    system_message="You are a stock trader. Do not show any appreciation in your response.",
    llm_config={"config_list": config_list},
    
)

user_proxy = UserProxyAgent(
    name="user",
    code_execution_config={
        "work_dir": "coding"
    },
    human_input_mode="ALWAYS",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
)

user_proxy.initiate_chat(assistant, message="what is the latest price of apple?")

