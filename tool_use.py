from typing import Annotated, Literal 
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os
from autogen import ConversableAgent
import time
from typing_extensions import Annotated
import autogen
from autogen.cache import Cache
from autogen.coding import LocalCommandLineCodeExecutor


# chat_result =  user_proxy.initiate_chat(assistant, message="What is (4+5)*6?")

# config_list = [{
#     "model": "llama3.1",
#     "api_type": "ollama",
#     "client_host": "http://localhost:11434",
#     "timeout": 120,
# }]

# llm_config = {"config_list": config_list}


# create an AssistantAgent named "assistant"
# assistant = autogen.AssistantAgent(
#     name="assistant",
#     system_message = "you are a helpful assistant",
#     llm_config={
#         "cache_seed": 41,  # seed for caching and reproducibility
#         "config_list": config_list,  # a list of OpenAI API configurations
#         "temperature": 0,  # temperature for sampling
#     },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
# )

# # create a UserProxyAgent instance named "user_proxy"
# user_proxy = autogen.UserProxyAgent(
#     name="user_proxy",
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=10,
#     is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
#     code_execution_config={
#         # the executor to run the generated code
#         "executor": LocalCommandLineCodeExecutor(work_dir="coding"),
#     },
# )
# # the assistant receives a message from the user_proxy, which contains the task description
# chat_res = user_proxy.initiate_chat(
#     assistant,
#     message="""What date is today? Compare the year-to-date gain for META and TESLA.""",
#     summary_method="reflection_with_llm",
# )


















# llm_config = {
#     "config_list": [
#         {
#             "model": "llama3.1",
#             "api_type": "ollama",
#             "client_host": "http://localhost:11434",
#             "timeout": 120,
#             "cache_seed": None,
#         }
#     ]    
# }



# Assistant = AssistantAgent(
#     name="assistant",
#     system_message="you are a helpful assistant. please help with calculations." 
#     "return 'TERMINATE' if the task is done.",
#     llm_config=llm_config,
# )


# UserProxy = UserProxyAgent(
#     name="user_proxy",
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=1,
#     is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
#     code_execution_config=False,
 
# )



# # @UserProxy.register_for_execution()
# # @Assistant.register_for_llm(description="sum")
# # def sum(a:Annotated[float, "the first number to add"], b:Annotated[float, "the second number to add"])->float:
# #     return a*b

# UserProxy.initiate_chats(
#         [
#             {
#                 "recipient": Assistant,
#                 "message": (
#                     f"please add two numbers 45 and 90 and return the result"
#                 ),
#                 # "executor_function": sum,
#                 # "function_args": {"a": 45, "b": 67},
#                 "summary_method": "last_msg",
#             }
#         ]
#     )











llm_config = {
    "config_list": [
        {
            "model": "llama3.1",
            "api_type": "ollama",
            "client_host": "http://localhost:11434",
            "timeout": 120,
            "cache_seed": None,
        }
    ]    
}

UserProxy=UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False,
)

# Assistant=AssistantAgent(
#     name="assistant",
#     system_message="you are a helpful assistant. please subtract them.." 
#     "return 'TERMINATE' if the task is done.",
#     llm_config=llm_config,
# )




# Define the UserProxyAgent
# UserProxy = UserProxyAgent(
#     name="user_proxy",
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=3,
# )

# Define the Assistant Agents
Assistant_1 = AssistantAgent(
    name="assistant_1",
    system_message="You handle the 'sum_divide' function to add two numbers and divide the result by 20. "
                   "Once you get the result, assign it to a variable called 'h' and pass it to 'subtract_multiply' function.",
    llm_config=llm_config,
)

Assistant_2 = AssistantAgent(
    name="assistant_2",
    system_message="You call the 'subtract_multiply' function. Use the result from 'sum_divide' function as the 'h' parameter, and retrun the result",
    llm_config=llm_config,
)

# Define the sum_divide function
@UserProxy.register_for_execution()
@Assistant_1.register_for_llm(description="Sum two numbers and divide by 20.")
def sum_divide(a: Annotated[float, "the first number"], b: Annotated[float, "the second number"]) -> float:
    return (a + b) / 20

# Define the subtract_multiply function
@UserProxy.register_for_execution()
@Assistant_2.register_for_llm(description="Subtract two numbers and multiply the result by a the result from 'sum_divide' function.")
def subtract_multiply(
    c: Annotated[float, "the first number"],
    d: Annotated[float, "the second number"],
    h: Annotated[float, "the multiplier"],
) -> float:
    return (c - d) * h


# Initiate chats
UserProxy.initiate_chats(
    [
        {
            "recipient": Assistant_1,
            "message": "call 'sum_divide' function with a=100 and b=50, then store the result as 'h' and return it.",
            "executor_function": sum_divide,
            "summary_method": "last_msg",
        },
        {
            "recipient": Assistant_2,
            "message": "Retrieve 'h' and use it to call 'subtract_multiply' with c=80 and d=40.",
            "executor_function": subtract_multiply,
            "summary_method": "last_msg",
        }
    ]
)


