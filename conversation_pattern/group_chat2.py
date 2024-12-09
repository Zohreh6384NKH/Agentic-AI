import autogen
import os
from autogen import GroupChat, GroupChatManager
from autogen import ConversableAgent


config_list = autogen.config_list_from_json(           #config_list_from_json is a function that load configuration for language models
    env_or_file = "OAI_CONFIG_LIST.json",              # specifies the source of configuration
    filter_dict = {                                    # apply a filter for a specific configuration
        "model": "gpt-4o",
    }
)
llm_config = {"config_list": config_list, "timeout":120}

number_agent = ConversableAgent(
    name="number_agent",
    system_message= "you return me the number i give you, each number in a line",
    llm_config= llm_config,
    human_input_mode="NEVER"
)

adder_agent = ConversableAgent(
    name="adder_agent",
    system_message="you add 1 to each number i give you and return me the number. one number each line",
    human_input_mode="NEVER",
    llm_config=llm_config

    
)

multiplier_agent = ConversableAgent(
    name="multiplier_agent",
    system_message="you multiply each number i give you by 4 and return me the number. one number each line",
    human_input_mode="NEVER",
    llm_config=llm_config

    
)

subtracter_agent = ConversableAgent(
    name="subtracter_agent",
    system_message="you subtract 3 from each number i give you and return me the number. one number each line",
    human_input_mode="NEVER",
    llm_config=llm_config

    
)

divider_agent = ConversableAgent(
    name="divider_agent",
    system_message="you divide each number i give you by 2 and return me the number. one number each line",
    human_input_mode="NEVER",
    llm_config=llm_config

    
)

group_chat = GroupChat(
    agents=[adder_agent, multiplier_agent, subtracter_agent, divider_agent, number_agent],
    messages=[],
    max_round=6,
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)

chat_result = number_agent.initiate_chat(
    group_chat_manager,
    message="My number is 12, I want to turn it into 3. work with different agent to get the result 3",
    summary_method="reflection_with_llm",
)                           