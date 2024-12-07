import autogen
import os


config_list = autogen.config_list_from_json(
    env_or_file = "OAI_CONFIG_LIST.json",
    filter_dict = {
        "model":["gpt-4o"]},
)

llm_config = {"config_list": config_list}

Assistant1 = autogen.ConversableAgent(
    name="number_agent",
    system_message="you are an agent is meant to write a quote about a famous author.",
    llm_config=llm_config,
    max_consecutive_auto_reply=1,
)

Assistant2= autogen.ConversableAgent(
    name="Assistant2",
    system_message="you are an agent that is meant to write a quote about the previous quote.",
    llm_config=llm_config,
    max_consecutive_auto_reply=1,
)

Assistant3 = autogen.ConversableAgent(
    name="Assistant3",
    system_message="you are an assistant agent who writes new quotes based on others.return 'TERMINATE'if the task is done",
    llm_config=llm_config,
    max_consecutive_auto_reply=1,
)
user_proxy = autogen.ConversableAgent(
    name="user_proxy",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config=False
    
    
)
user_proxy.initiate_chats(
    [
    
        {
            "recipient": Assistant1,
            "message": "you write a famous qutoe about a famous author",
            "max_turns": 2,
            "summary_method": "reflection_with_llm",      
        },
        
        {
            "recipient": Assistant2,
            "message": "write a quote about a famous author",
            "clear_history": True, 
            "silent": False,
            "summary_method": "reflection_with_llm",       
        },
        {
            
            "recipient": Assistant3,
            "message": "write a quote about a famous author",
            "clear_history": True, 
            "silent": False,
            "summary_method": "reflection_with_llm",       
        }
        
  ]  )
