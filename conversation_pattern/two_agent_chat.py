import os
from autogen import ConversableAgent



student_agent = ConversableAgent(
    "student",
    system_message="You are a student willing to learn.",
    llm_config={"config_list": [{"model": "gpt-4", "temperature": 0.7, "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  # Never ask for human input.
)

teacher_agent = ConversableAgent(
    "teacher",
    system_message="you are a math teacher.",
    llm_config={"config_list": [{"model": "gpt-4", "temperature": 0.7, "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  # Never ask for human input.
)

result = student_agent.initiate_chat(
    teacher_agent,
    message="I am a student. I need some help with my homework.",
    max_turns=2,
    summary_method="reflection_with_llm")
print(result)