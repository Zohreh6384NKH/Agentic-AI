

import os
import requests
from typing import Annotated, Dict, List

def list_files_by_folder(repo_url: Annotated[str, "The URL of the GitHub repository"]) -> Dict[str, List[str]]:
    """
    Recursively list all files in a GitHub repository and group them by folder.

    Args:
        repo_url (str): The URL of the GitHub repository (e.g., "https://github.com/owner/repo").
    
    Returns:
        Dict[str, List[str]]: A dictionary where keys are folder paths, and values are lists of file names.

    Raises:
        Exception: If the API request fails or authentication is invalid.
    """
    def fetch_contents(api_url, headers, folder_structure, current_path=""):
        """
        Recursive function to fetch files and directories from a given API endpoint.
        """
        response = requests.get(api_url, headers=headers)
        print(response)
        print(response.json())
        if response.status_code == 200:
            for item in response.json():
                if item["type"] == "file":
                    # Group files by folder
                    folder_structure.setdefault(current_path, []).append(item["name"])
                elif item["type"] == "dir":
                    # Recursive call for subdirectories
                    fetch_contents(item["url"], headers, folder_structure, f"{current_path}/{item['name']}".strip("/"))
        else:
            raise Exception(f"Failed to fetch contents: {response.status_code} - {response.json().get('message', '')}")

    # Prepare headers for GitHub API authentication
    owner, repo_name = repo_url.split("/")[-2:]
    base_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}

    folder_structure = {}
    fetch_contents(base_api_url, headers, folder_structure)
    return folder_structure


# Example Usage
if __name__ == "__main__":
    # repo_url = "https://github.com/facebookresearch/dinov2"
    repo_url = "https://github.com/Zohreh6384NKH/Agentic-AI"  # Replace with your repository URL
    
    try:
        folder_files = list_files_by_folder(repo_url)
        print("\nFiles Organized by Folders:\n")
        for folder, files in folder_files.items():
            print(f"Folder: {folder if folder else '/'}")
            for file in files:
                print(f"   - {file}")
    except Exception as e:
        print("Error:", e)