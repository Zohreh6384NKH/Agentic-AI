import autogen
import os
import json
from autogen import ConversableAgent
import requests
import base64

def main():
    config_list = autogen.config_list_from_json(
        env_or_file = "OAI_CONFIG_LIST.json"
    )
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={"config_list": config_list},
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user",
        human_input_mode="NEVER",

        code_execution_config=
        {
            "use_docker": True,
            "work_dir": "coding",
        })
    
    
    user_proxy.initiate_chat(assistant, message="please write the code for calculating binary search in python with an example")
    
if __name__ == "__main__":
    main()
    
    
    
