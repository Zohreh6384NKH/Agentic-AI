import autogen
import os
import json
from autogen import ConversableAgent
import requests
import base64




def fetch_profile(repo_url):
    """
    Fetch the profile metadata of a specified GitHub repository.

    Args:
    repo_url (str): The URL of the repository to fetch.

    Returns:
    dict: Repository profile metadata or an error message.
    """
    owner, repo_name = repo_url.split("/")[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = requests.get(api_url, headers={"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"})
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch repository profile. Status code: {response.status_code}"}

github_fetcher_agent = ConversableAgent(
    name="GitHub_Fetcher_Agent",
    system_message="You fetch GitHub repository profiles based on a given URL.",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    function_map={"fetch_profile": fetch_profile},
    human_input_mode="NEVER"
)




def list_files(repo_data):
    
    """
    List all files in a given GitHub repository.

    Args:
    repo_data (dict): Repository profile metadata.

    Returns:
    list: List of file paths in the repository or an error message.
    """
    if "contents_url" not in repo_data:
        return {"error": "Repository data does not include contents URL"}
    contents_url = repo_data["contents_url"].replace("{+path}", "")
    response = requests.get(contents_url, headers={"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"})
    if response.status_code == 200:
        return [item["path"] for item in response.json() if item["type"] == "file"]
    else:
        return {"error": f"Failed to list files. Status code: {response.status_code}"}

file_listing_agent = ConversableAgent(
    name="File_Listing_Agent",
    system_message="You list all files in a GitHub repository.",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    function_map={"list_files": list_files},
    human_input_mode="NEVER"
)




def fetch_file_content(repo_url, file_list):
    """
    Fetch content for a list of files in a GitHub repository.

    Args:
    repo_url (str): The repository URL.
    file_list (list): List of file paths.

    Returns:
    dict: File contents or an error message.
    """
    owner, repo_name = repo_url.split("/")[-2:]
    base_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    contents = {}
    for file_path in file_list:
        response = requests.get(f"{base_url}/{file_path}", headers={"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"})
        if response.status_code == 200:
            file_data = response.json()
            contents[file_path] = base64.b64decode(file_data["content"]).decode("utf-8")
        else:
            contents[file_path] = {"error": f"Failed to fetch content for {file_path}"}
    return contents
content_fetcher_agent = ConversableAgent(
    name="Content_Fetcher_Agent",
    system_message="You fetch file content from a GitHub repository.",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    function_map={"fetch_file_content": fetch_file_content},
    human_input_mode="NEVER"
)

# Define Summarizer Agent
def summarize_content(contents):
    """
    Summarize the contents of files.

    Args:
    contents (dict): Dictionary of file paths to content.

    Returns:
    dict: Dictionary of file paths to summaries.
    """
    return {file: f"Summary of {content[:20]}..." for file, content in contents.items()}

summarizer_agent = ConversableAgent(
    name="Summarizer_Agent",
    system_message="You summarize the contents of files.",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    function_map={"summarize_content": summarize_content},
    human_input_mode="NEVER"
)




# Sequential Workflow without 'None' Recipient Issue
repo_url = "https://github.com/Zohreh6384NKH/Agentic-AI"

# Initial sequential chats for the first three steps
chat_results = github_fetcher_agent.initiate_chats(
    [
        # Step 1: GitHub Fetcher Agent fetches metadata
        {
            "recipient": file_listing_agent,
            "message": f"fetch_profile: {repo_url}",
            "max_turns": 1,
            "summary_method": "last_msg",
        },
        # Step 2: File Listing Agent lists files
        {
            "recipient": content_fetcher_agent,
            "message": "list_files: These are the repository details you provided.",
            "max_turns": 1,
            "summary_method": "last_msg",
        },
        # Step 3: File Content Fetcher Agent fetches file contents
        {
            "recipient": summarizer_agent,
            "message": "fetch_file_content: These are the file paths.",
            "max_turns": 1,
            "summary_method": "last_msg",
        },
    ]
)

# Extract the file contents output from the summarizer agent
# Assuming the output of the third step is file contents
file_contents_result = chat_results[-1]  # Get the result of the last processed chat

# Handle the final summarization step manually
final_summary = summarizer_agent.generate_reply(
    messages=[{"content": f"summarize_content: {file_contents_result}", "role": "user"}]
)

# Output the final summaries
print("Final Summary:")
print(final_summary)