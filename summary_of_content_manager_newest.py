
import autogen
from autogen import UserProxyAgent, AssistantAgent, config_list_from_json, GroupChat, GroupChatManager
from typing import Annotated
import os
import requests
import base64
import json



config_list = [{
    "model": "llama3.1",
    "api_type": "ollama",
    "client_host": "http://localhost:11434",
    "timeout": 30
}]

llm_config = {"config_list": config_list}


# Define the agents
file_listing_agent = AssistantAgent(
    name="file_listing_agent",
    system_message="You execute the list_files function and return the list of files in the repository.",
    llm_config=llm_config,
    
)

content_fetcher_agent = AssistantAgent(
    name="content_fetcher_agent",
    system_message="You execute the fetch_file_content function and return the content of the specified files in the repository",
    llm_config=llm_config,
)

summarizer_agent = AssistantAgent(
    name="summarizer_agent",
    system_message="You summarize the  the content of each specified files in the repository",
    llm_config=llm_config
)

UserProxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config=False
)


    
# define the functions to be executed by agents
@UserProxy.register_for_execution()
@file_listing_agent.register_for_llm(description="List all files in a Github repository.")
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
    """
    Fetch content of files from the GitHub repository and return a dictionary 
    with file names as keys and their content as values.
    """
    owner, repo_name = repo_url.split("/")[-2:]
    base_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}
    file_contents = {}

    for file_path in files_list:
        response = requests.get(f"{base_url}/{file_path}", headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            file_name = file_path.split("/")[-1]  # Extract the file name from the path
            file_contents[file_name] = base64.b64decode(file_data["content"]).decode("utf-8")
        else:
            file_name = file_path.split("/")[-1]  # Extract the file name from the path
            file_contents[file_name] = f"Failed to fetch content: {response.status_code}"
    
    return file_contents


@UserProxy.register_for_execution()
@summarizer_agent.register_for_llm(description="summarize the content of files .")
def summarize_content(file_contents: Annotated[dict, "Dictionary where keys are file names and values are file contents"]) -> dict:
    """
    Summarize the content of files and return a dictionary with file names as keys and their summaries as values.

    Args:
        contents (dict): A dictionary where keys are file names and values are file contents.

    Returns:
        dict: A dictionary with file names as keys and summarized content as values.
    """
    summaries = {}
    for file_name, content in file_contents.items():
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
                "message": "Please follow these steps sequentially:"

                "1. list all files in the repository: https://github.com/Zohreh6384NKH/python_coding/ML_coding. Return the list of file paths."

               " 2. fetch the content of the listed files from the repository using the `fetch_file_content` function. Return a dictionary where the keys are file names and the values are their respective contents."

                "3. summarize the values from the dictionary returned. Use the `summarize_content` function to generate a concise summary for each file. Return a final dictionary where the keys are file names and the values are their summaries.",

            "silent": False,
            "summary_method": "last_msg",
        }
    ]
)





