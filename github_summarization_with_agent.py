import autogen
from autogen import UserProxyAgent, AssistantAgent, config_list_from_json
from typing import Dict, List, Annotated
import chardet
from typing import Annotated
import os
import requests
import base64
import json
import git




# Define LLM Configuration
config_list = [{
    "model": "llama3.1",
    "api_type": "ollama",
    "client_host": "http://localhost:11434",
    "timeout": 120
}]

llm_config = {"config_list": config_list}

# Define Agents
summarizer_agent = AssistantAgent(
    name="summarizer_agent",
    system_message="You summarize the content of a list of file contents in 3 concise sentences for each file.",
    llm_config=llm_config
)

UserProxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    code_execution_config=False
)

# Clone repository function
# Clone repository function
def clone_repository(repo_url: str, clone_dir: str) -> str:
    """
    Clone the given repository to the specified directory.
    """
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)
        
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(clone_dir, repo_name)

    if not os.path.exists(repo_path):
        print(f"Cloning repository from {repo_url} to {repo_path}...")
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Repository cloned successfully to {repo_path}.")
    else:
        print(f"Repository already exists at {repo_path}.")

    return repo_path


# List files grouped by folders
def list_files_by_folders(repo_dir: str) -> Dict[str, List[str]]:
    """
    List all files in a directory and organize them by folders.
    """
    files_by_folders = {}

    for root, _, files in os.walk(repo_dir):
        # Skip hidden directories like .git
        if ".git" in root.split(os.sep):
            continue

        # Get relative folder path from the repository root
        relative_folder = os.path.relpath(root, repo_dir)
        if relative_folder == ".":
            relative_folder = ""  # Represent the root folder as an empty string

        # Add files to the appropriate folder
        files_by_folders[relative_folder] = [os.path.join(relative_folder, file) for file in files]

    return files_by_folders


# Read files and organize their content
def read_files(files_by_folder: Dict[str, List[str]], repo_path: str) -> Dict[str, Dict[str, str]]:
    """
    Read the content of all files in the repository.
    """
    content_by_folder = {}
    for folder, files in files_by_folder.items():
        folder_content = {}
        for file_path in files:
            full_file_path = os.path.join(repo_path, file_path)  # Construct the full file path
            try:
                with open(full_file_path, "rb") as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
                    content = raw_data.decode(encoding)
                    folder_content[os.path.basename(file_path)] = content  # Store file name and content
            except Exception as e:
                folder_content[os.path.basename(file_path)] = f"Error reading file: {e}"
        content_by_folder[folder] = folder_content
    return content_by_folder



        

@UserProxy.register_for_execution()
@summarizer_agent.register_for_llm(description="Summarize the content of files organized by folders.")# Summarize content function
def summarize_content(content_by_folder: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Summarize the content of files and return a dictionary with summaries.
    """
    summaries_by_folder = {}
    for folder, files in content_by_folder.items():
        folder_summaries = {}
        for file_name, content in files.items():
            if isinstance(content, str):  # Ensure content is a valid string
                try:
                    # Create a summarization prompt
                    prompt = (
                        f"Summarize the following content of the file '{file_name}' in 3-4 concise sentences:\n\n"
                        f"{content}"
                    )

                    # Call the summarizer agent to generate the summary
                    llm_response = summarizer_agent.generate_reply(messages=[{"role": "user", "content": prompt}])

                    # Check if the response is valid and contains the expected content
                    if isinstance(llm_response, dict) and "content" in llm_response:
                        folder_summaries[file_name] = llm_response["content"]
                    else:
                        folder_summaries[file_name] = f"Unexpected response format: {llm_response}"
                except Exception as e:
                    folder_summaries[file_name] = f"Error summarizing content: {str(e)}"
            else:
                folder_summaries[file_name] = "Invalid content format or failed to fetch."
        summaries_by_folder[folder] = folder_summaries
    return summaries_by_folder






if __name__ == "__main__":
    
    
    repo_url = "https://github.com/Zohreh6384NKH/Agentic-AI.git"  # Replace with your desired repository URL
    clone_dir = "./clone_repo/my_repository"

    # Step 1: Clone the repository
    # repo_path = clone_repository(repo_url, clone_dir)
    repo_path = "./clone_repo/my_repository/Agentic-AI"

    # Step 2: List all files grouped by folders
    list_of_files = list_files_by_folders(repo_path)

    # Step 3: Read the content of all files
    content_by_folder = read_files(list_of_files, repo_path)

    

    # Step 4: Use agents to summarize the file contents
    # Summarize the file contents using the summarizer agent
summaries = UserProxy.initiate_chats(
    [
        {
            "recipient": summarizer_agent,
            "message": (
                "You are provided with a dictionary `content_by_folder`"
                "Your task is to summarize each file's content in 3-4 concise sentences. you use the `summarize_content` function. "
                "Please return the summaries as a dictionary with the same structure: folder names as keys, and their values being "
                "dictionaries where the keys are file names and the values are their respective summaries.\n\n"
                "Here is the `content_by_folder` dictionary:\n"
                f"{json.dumps(content_by_folder, indent=4)}\n\n"
                "Ensure that the summaries are concise, accurate, and well-structured. "
            ),
            "args": {"content_by_folder": content_by_folder},  # Explicitly pass file contents
            "silent": False,
            "summary_method": "last_msg",
        }
    ]
)



