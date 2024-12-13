import autogen
from autogen import UserProxyAgent, AssistantAgent, config_list_from_json, GroupChat, GroupChatManager
from typing import Annotated
import os
import requests
import base64
import json




# Load configuration for agents
config_list = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST.json",
    filter_dict={"model": "gpt-4o"},
)
llm_config = {"config_list": config_list}

# Define the agents
file_listing_agent = AssistantAgent(
    name="file_listing_agent",
    system_message="You execute the list_files function and return the list of files in the repository.",
    llm_config=llm_config,
)

content_fetcher_agent = AssistantAgent(
    name="content_fetcher_agent",
    system_message="You execute the fetch_file_content function and return the content of the specified files in the repository.",
    llm_config=llm_config,
)

summarizer_agent = AssistantAgent(
    name="summarizer_agent",
    system_message="You execute the summarize function and return the summary of the content of each specified files in the repository.",
    llm_config=llm_config,
)

UserProxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=2,
    code_execution_config=False,
)


# Define the functions to be executed by agents
@UserProxy.register_for_execution()
@file_listing_agent.register_for_llm(description="List all files in a GitHub repository.")
def list_files(repo_url: Annotated[str, "The URL of the GitHub repository"]) -> list:
    owner, repo_name = repo_url.split("/")[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        files = [item["path"] for item in response.json() if item["type"] == "file"]
        return files
    else:
        raise Exception(f"Failed to list files: {response.status_code}")


@UserProxy.register_for_execution()
@content_fetcher_agent.register_for_llm(description="Fetch content of files from a GitHub repository.")
def fetch_file_content(repo_url: Annotated[str, "The repository URL"], files_list: Annotated[list, "List of file paths"]) -> dict:
    owner, repo_name = repo_url.split("/")[-2:]
    base_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}
    contents = {}
    for file_path in files_list:
        response = requests.get(f"{base_url}/{file_path}", headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            contents[file_path] = base64.b64decode(file_data["content"]).decode("utf-8")
        else:
            contents[file_path] = f"Failed to fetch content: {response.status_code}"
    return contents




@UserProxy.register_for_execution()
@summarizer_agent.register_for_llm(description="Summarize the contents of files fetched from a GitHub repository.")
def summarize_content(
    contents: Annotated[dict[str, str], "A dictionary where keys are file names and values are the content of those files."]) -> dict[str, str]:
    """
    Summarize the contents of files.

    Args:
    repo_url (str): The URL of the repository.
    contents (dict): A dictionary where keys are file paths and values are the content of those files.

    Returns:
    dict: A dictionary where keys are file paths and values are the summaries of their content.
    """
    summaries = {}
    for file_name, content in contents.items():
        if isinstance(content, str):  # Ensure content is a valid string
            try:
                # Create a summarization prompt
                prompt = (
                    f"Summarize the following content of the file '{file_name}' in 3 concise sentences:\n\n"
                    f"{content}"
                )

                # Call the summarizer agent to generate the summary
                llm_response = summarizer_agent.generate_reply(messages=[{"role": "user", "content": prompt}])

                # Check if the response is valid and contains the expected content
                if isinstance(llm_response, dict) and "content" in llm_response:
                    summaries[file_name] = llm_response["content"]
                else:
                    summaries[file_name] = f"Unexpected response format: {llm_response}"
            except Exception as e:
                summaries[file_name] = f"Error summarizing content: {str(e)}"
        else:
            summaries[file_name] = "Invalid content format or failed to fetch."
    return summaries


groupchat = GroupChat(agents=[UserProxy, file_listing_agent, content_fetcher_agent, summarizer_agent], messages=[], max_round=12)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

UserProxy.initiate_chats(
    [
        {
            "recipient": manager,
            "message": "message": "Please list all files in the repository: https://github.com/Zohreh6384NKH/AutoGen_tutorial"
            "and fetch the content of the files by the file_listing_agent.then you summarize the content of each file name and return two sentences summary.",
            "clear_history": False,
            "silent": False,
            "summary_method": "last_msg",
        }
        
    ]
)



