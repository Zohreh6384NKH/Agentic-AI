
import os
import requests
import base64
from autogen import ConversableAgent
import json




# Define GitHub Fetcher Agent
github_agent = ConversableAgent(
    name="github_agent",
    system_message="You are a GitHub Fetcher Agent. Your tasks include fetching metadata "
                   "about GitHub repositories, listing files in a repository, fetching file content, "
                   "and summarizing the content of those files.",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  # Never ask for human input.
)

# Global Headers for Authentication
headers = {
    "Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"  # Use your GitHub token
}

# Skill: Fetch Repository Profile
def fetch_profile(repo_url):
    """
    Fetch the profile of a given GitHub repository.

    Args:
    repo_url (str): The URL of the repository to fetch, e.g., "https://github.com/owner/repo".

    Returns:
    dict: The JSON representation of the repository profile metadata if the request is successful.

    Raises:
    Exception: If the API request fails with a status code other than 200.
    """
    owner, repo_name = repo_url.split("/")[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Repository profile metadata
    else:
        raise Exception(f"Failed to fetch repository profile. Status code: {response.status_code}")
    
    
    
    

# Skill: List Repository Files
def list_files(repo_url):
    """
    List files in a given GitHub repository.

    Args:
    repo_url (str): The URL of the repository to list files from, e.g. "https://github.com/owner/repo".

    Returns:
    list: List of file names in the repository, including files in subdirectories.
    dict: A dictionary containing an error message if the API request fails, e.g. {"error": "Failed to list files: 404"}.

    Raises:
    Exception: If the API request fails with a status code other than 200.
    """
    owner, repo_name = repo_url.split("/")[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        files = []
        for item in response.json():
            if item["type"] == "file":
                files.append(item["path"])
            elif item["type"] == "dir":
                # Recursive call for directories
                nested_files = list_files(f"{repo_url}/{item['path']}")
                if isinstance(nested_files, list):
                    files.extend(nested_files)
        return files
    else:
        return {"error": f"Failed to list files: {response.status_code}"}

# Skill: Fetch File Content


def fetch_file_content(repo_url, file_path):
    """
    Fetch the content of a file from a given GitHub repository using the GitHub API.
    """
    owner, repo_name = repo_url.split("/")[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        if "content" in file_data:
            # File content is base64-encoded; decode it
            return base64.b64decode(file_data["content"]).decode("utf-8")
        else:
            return {"error": "No content field found in API response"}
    elif response.status_code == 404:
        return {"error": f"File not found: {file_path}"}
    elif response.status_code == 403:
        return {"error": f"Access denied or rate-limited. Ensure proper authentication."}
    else:
        return {"error": f"Failed to fetch file content. Status code: {response.status_code}"}
    
    
    
    
    
    
    

# Skill: Summarize File Content Using the Agent
def summarize_file_content(agent, repo_url, file_list, max_chars=3000):
    """
    Summarize the content of a list of files in a given GitHub repository using an agent.

    Args:
    agent (ConversableAgent): The agent used to generate the summary.
    repo_url (str): The URL of the repository to summarize, e.g. "https://github.com/Zohreh6384NKH/MachineLearning_bank-marketing".
    file_list (list): List of file names to summarize, including files in subdirectories.
    max_chars (int, optional): Maximum number of characters to read from each file. Defaults to 3000.

    Returns:
    dict: Dictionary where the keys are the file paths and the values are the summaries of the file content.
    """
    summaries = {}
    for file_path in file_list:
        print(f"\nFetching content for file: {file_path}")
        file_content = fetch_file_content(repo_url, file_path)
        if isinstance(file_content, dict) and "error" in file_content:
            summaries[file_path] = file_content["error"]
            print(f"Error fetching file: {file_path} - {file_content['error']}")
            continue
        
        # Truncate the file content
        truncated_content = file_content[:max_chars]
        print(f"Truncated content (first 200 chars): {truncated_content[:200]}...")
        
        # Prepare the message for the agent
        message = (
            f"Summarize the following file content in exactly two sentences:\n\n"
            f"{truncated_content}\n\nSummary:"
        )
        
        # Use the agent to generate a summary
        try:
            response = agent.generate_reply(messages=[{"content": message, "role": "user"}])
            summaries[file_path] = response
        except Exception as e:
            summaries[file_path] = f"Error during summarization: {e}"
            print(f"Error summarizing file: {file_path} - {e}")
    
    return summaries





# Example Workflow
try:
    repo_url = "https://github.com/Zohreh6384NKH/Agentic-AI"

    # Step 1: Fetch Profile
    profile = fetch_profile(repo_url)
    print("Repository Profile:")
    print(json.dumps(profile, indent=4))

    # Step 2: List Files
    file_list = list_files(repo_url)
    if isinstance(file_list, dict) and "error" in file_list:
        print(f"Error listing files: {file_list['error']}")
    else:
        print("\nList of Files:")
        print(file_list)

        # Step 3: Summarize Files with Two-Sentence Summary
        summaries = summarize_file_content(github_agent, repo_url, file_list)
        for file_path, summary in summaries.items():
            print(f"\nTwo-Sentence Summary for {file_path}:\n{summary}")
except Exception as e:
    print(f"Error: {e}")