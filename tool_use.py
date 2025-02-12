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




























#define two function  and two agents and pass output from first function to second function and call it


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

# UserProxy = UserProxyAgent(
#     name="user_proxy",
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=1,
#     code_execution_config=False,
# )

# Assistant_1 = AssistantAgent(
#     name="assistant_1",
#     system_message="First, call the 'sum_divide' function"
#                    "store the output of function to 'h'. then call 'subtract_multiply' function and pass the value of 'h' to this function. "
#                    "be sure not to modify or generate a new value for 'h'.",
                   
#     llm_config=llm_config,
# )

# # Define the sum_divide function
# @UserProxy.register_for_execution()
# @Assistant_1.register_for_llm(description="Sum two numbers and divide by 5.")
# def sum_divide(a: float, b: float) -> float:
#     return (a + b) / 5

# # Define the subtract_multiply function
# @UserProxy.register_for_execution()
# @Assistant_1.register_for_llm(description="Subtract two numbers and multiply by the result from 'sum_divide' function.")
# def subtract_multiply(c: float, d: float, h: float) -> float:
#     return (c - d) * h

# # Initiate the chats with strict linking
# UserProxy.initiate_chats(
#     [
#         {
#             "recipient": Assistant_1,
#             "message": "First, call 'sum_divide' function with a=100 and b=50, store the result as 'h' and return the result of function, second, call 'subtract_multiply' function with the value of c=80 and d=40 and 'h' as output of function",
#             "executor_function": sum_divide,
#             "summary_method": "last_msg",
#         }
#     ]
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

# UserProxy = UserProxyAgent(
#     name="user_proxy",
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=1,
#     code_execution_config=False,
# )

# Assistant_1 = AssistantAgent(
#     name="assistant_1",
#     system_message="Step 1: Call the 'sum_divide' function with a=100 and b=50. "
#                    "Store the result as 'h' exactly as returned by the function. "
#                    ,
#     llm_config=llm_config,
# )

# Assistant_2 = AssistantAgent(
#     name="assistant_2",
#     system_message="Step 2: Use the exact value of 'h' from the previous step to call the 'subtract_multiply' function. "
#                    "Call 'subtract_multiply' with c=80 and d=40 and 'h' as output of function. "
#                    "Return the final result. ",
#     llm_config=llm_config,
# )

# # Define the sum_divide function
# @UserProxy.register_for_execution()
# @Assistant_1.register_for_llm(description="Sum two numbers and divide by 5.")
# def sum_divide(a: float, b: float) -> float:
#     """
#     Sums two numbers and divides the result by 5.

#     Parameters:
#     a (float): The first number.
#     b (float): The second number.

#     Returns:
#     h (float): The result of (a + b) divided by 5.
#     """
#     return (a + b) / 5

# # Define the subtract_multiply function
# @UserProxy.register_for_execution()
# @Assistant_2.register_for_llm(description="Subtract two numbers and multiply by the result from 'sum_divide'.")
# def subtract_multiply(c: float, d: float, h: float) -> float:
#     """
#     Subtracts two numbers and multiplies the result by the output of the 'sum_divide' function.

#     Parameters:
#     c (float): The first number.
#     d (float): The second number.
#     h (float): The output of the 'sum_divide' function.

#     Returns:
#     float: The result of (c - d) multiplied by h.
#     """
#     return (c - d) * h

# # Initiate the chats with strict linking of 'h'
# UserProxy.initiate_chats(
#     [
#         {
#             "recipient": Assistant_1,
#             "message": "Step 1: Call 'sum_divide' function with a=100 and b=50, store the result as 'h' and always use this value, and return the value.",
#             "executor_function": sum_divide,
#             "summary_method": "last_msg",
#         },
#         {
#             "recipient": Assistant_2,
#             "message": "Step 2: use the value of 'h' and call 'subtract_multiply' with c=80 and d=40. Return the result.",
#             "executor_function": subtract_multiply,
#             "summary_method": "last_msg",
#         }
#     ]
# )

























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

UserProxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    code_execution_config=False,
)

Assistant_1 = AssistantAgent(
    name="assistant_1",
    system_message="Step 1: Call the 'sum_divide' function with a=100 and b=50. "
                   "Store the result as 'h' (a numeric value). "
                   "This value of 'h' must be passed exactly as a number to the next function.",
    llm_config=llm_config,
)

Assistant_2 = AssistantAgent(
    name="assistant_2",
    system_message="Step 2: Use the numeric value of 'h' as returned by 'sum_divide'. "
                   "Call 'subtract_multiply' with c=80 and d=40 using 'h' as the exact numeric input. "
                   "Do not pass symbolic references or modify the value of 'h'. Return the result.",
    llm_config=llm_config,
)

# Define the sum_divide function
@UserProxy.register_for_execution()
@Assistant_1.register_for_llm(description="Sum two numbers and divide by 5.")
def sum_divide(a: float, b: float) -> float:
    return (a + b) / 5

# Define the subtract_multiply function
@UserProxy.register_for_execution()
@Assistant_2.register_for_llm(description="Subtract two numbers and multiply by the result from 'sum_divide' function.")
def subtract_multiply(c: float, d: float, h: float) -> float:
    return (c - d) * h

# Initiate the chats with strict numeric linking of 'h'
UserProxy.initiate_chats(
    [
        {
            "recipient": Assistant_1,
            "message": "Step 1: Call 'sum_divide' function with a=100 and b=50, store the result from function as 'h', and return it.",
            "executor_function": sum_divide,
            "summary_method": "last_msg",
        },
        {
            "recipient": Assistant_2,
            "message": "Step 2: Use the value of 'h' to call 'subtract_multiply' function with c=80 and d=40. Return the result.",
            "executor_function": subtract_multiply,
            "summary_method": "last_msg",
        }
    ]
)










