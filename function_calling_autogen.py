
import autogen
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from typing import Annotated
import random
from autogen import GroupChat, GroupChatManager
import json



config_list = config_list_from_json(
    env_or_file = "OAI_CONFIG_LIST.json",
    filter_dict = {
        "model": "gpt-4o",
    }
)
llm_config = {"config_list": config_list, "timeout":120}
        
#create assistant agent
assistant1 = AssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message="you are to save to a file",
)
assistant2 = AssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message="you are to save to a file",
)



#create user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    max_consecutive_auto_reply=10,
    code_execution_config=False
)

@user_proxy.register_for_execution()
@assistant1.register_for_llm(description="save to a file")
@assistant2.register_for_llm(description="save to a file")
def save_to_file(message:Annotated[str, "the response from the model"])->str:
    print(message)
    random_number = random.randint(1, 1000)
    with open("saved_file_"+str(random_number)+".txt", "w") as file:
        file.write(message)
    return message



group_chat = autogen.GroupChat(agents=[user_proxy, assistant1, assistant2], messages=[], max_round=12)

manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)
        
  
user_proxy.initiate_chats(
    [
        {
            "recipient": assistant1,
            "message": "write a quote about a famous author",
            "clear_history": True, 
            "silent": False,
            "summary_method": "last_msg",
        },
        {
          "recipient": assistant2,
            "message": "give me a quote from a different famous author",
            "summary_method": "reflection_with_llm",
        },
    ]

    )