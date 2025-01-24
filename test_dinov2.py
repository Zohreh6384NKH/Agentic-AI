import os
import chardet
from typing import Dict, List



# the best code for listing and reading files

# import os
# import chardet
# from typing import Dict, List

# # Function to list all files and folders
# def list_all_files_and_folders(repo_dir: str) -> Dict[str, List[str]]:
#     """
#     Recursively list all files and folders in a directory, including all levels of subdirectories.

#     Args:
#         repo_dir (str): The root directory of the repository.

#     Returns:
#         Dict[str, List[str]]: A dictionary where keys are folder paths relative to the root directory,
#                               and values are lists of file names in those folders.
#     """
#     files_by_folders = {}
#     for root, _, files in os.walk(repo_dir):
#         # Ensure no folders are skipped, even empty ones
#         relative_folder = os.path.relpath(root, repo_dir)
#         if relative_folder == ".":
#             relative_folder = "Root"  # Represent the root folder as "Root"
#         files_by_folders[relative_folder] = files
#     return files_by_folders

# # Function to read the content of all files
# def read_files_content(files_by_folder: Dict[str, List[str]], repo_path: str) -> Dict[str, Dict[str, str]]:
#     """
#     Read the content of all files in the repository.

#     Args:
#         files_by_folder (Dict[str, List[str]]): Dictionary of files grouped by folder.
#         repo_path (str): Path to the repository.

#     Returns:
#         Dict[str, Dict[str, str]]: Dictionary where keys are folder paths and values are dictionaries 
#                                    with file names as keys and file contents as values.
#     """
#     content_by_folder = {}
#     for folder, files in files_by_folder.items():
#         folder_content = {}
#         for file_name in files:
#             # Construct the full file path
#             file_path = os.path.join(repo_path, folder, file_name) if folder != "Root" else os.path.join(repo_path, file_name)
#             try:
#                 # Ensure file exists before reading
#                 if not os.path.exists(file_path):
#                     folder_content[file_name] = "File does not exist"
#                     continue

#                 # Read the file content
#                 with open(file_path, "rb") as f:
#                     raw_data = f.read()
#                     # Detect encoding and decode content
#                     detected_encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
#                     content = raw_data.decode(detected_encoding, errors="ignore")  # Ignore decoding errors
#                     folder_content[file_name] = content
#             except Exception as e:
#                 folder_content[file_name] = f"Error reading file: {e}"
#         content_by_folder[folder] = folder_content
#     return content_by_folder

# # Function to summarize the content of files
# def summarize_content_as_dict(content_by_folder: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
#     """
#     Summarize the content of files and return a dictionary with file names as keys and their summaries as values.

#     Args:
#         content_by_folder (Dict[str, Dict[str, str]]): Dictionary where keys are folder paths and values are dictionaries
#                                                       with file names as keys and file contents as values.

#     Returns:
#         Dict[str, Dict[str, str]]: Dictionary with folder paths as keys and dictionaries with file names and summaries as values.
#     """
#     summaries_by_folder = {}
#     for folder, files in content_by_folder.items():
#         folder_summaries = {}
#         for file_name, content in files.items():
#             if isinstance(content, str):  # Ensure content is a valid string
#                 try:
#                     # Create a summarization prompt
#                     prompt = (
#                         f"Summarize the following content of the file '{file_name}' in 3 concise sentences:\n\n"
#                         f"{content[:2000]}"  # Truncate to avoid exceeding token limits
#                     )

#                     # Call the summarizer (simulate summarization with a placeholder)
#                     # Replace this with the actual summarizer function or API call
#                     summary = f"Summary of {file_name}: This is a placeholder for the summary of the content."  # Replace with summarization API
                    
#                     folder_summaries[file_name] = summary
#                 except Exception as e:
#                     folder_summaries[file_name] = f"Error summarizing content: {str(e)}"
#             else:
#                 folder_summaries[file_name] = "Invalid content format or failed to fetch."
#         summaries_by_folder[folder] = folder_summaries
#     return summaries_by_folder

# if __name__ == "__main__":
#     repo_path = "./clone_repo/dinov2_repo/dinov2"  # Change this to your repository's path

#     # Step 1: List all files and folders (including all nested levels)
#     files_by_folder = list_all_files_and_folders(repo_path)
#     print("Files by folders:")
#     for folder, files in files_by_folder.items():
#         print(f"Folder: {folder}")
#         for file in files:
#             print(f"  - {file}")

   














import os
import chardet
from typing import Dict, List
from autogen import AssistantAgent


# Define LLM Configuration
config_list = [{
    "model": "llama3.1",
    "api_type": "ollama",
    "client_host": "http://localhost:11434",
    "timeout": 120
}]

llm_config = {"config_list": config_list}

# Define the summarizer agent
summarizer_agent = AssistantAgent(
    name="summarizer_agent",
    system_message="You summarize the content of each fetched file in 3-4 concise sentences.",
    llm_config=llm_config
)




# Function to list all files and folders
def list_all_files_and_folders(repo_dir: str) -> Dict[str, List[str]]:
    """
    Recursively list all files and folders in a directory, including all levels of subdirectories.

    Args:
        repo_dir (str): The root directory of the repository.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are folder paths relative to the root directory,
                              and values are lists of file names in those folders.
    """
    files_by_folders = {}
    for root, _, files in os.walk(repo_dir):
        # Ensure no folders are skipped, even empty ones
        relative_folder = os.path.relpath(root, repo_dir)
        if relative_folder == ".":
            relative_folder = "Root"  # Represent the root folder as "Root"
        files_by_folders[relative_folder] = files
    return files_by_folders






# Function to read the content of all files
def read_files_content(files_by_folder: Dict[str, List[str]], repo_path: str) -> Dict[str, Dict[str, str]]:
    """
    Read the content of all files in the repository.

    Args:
        files_by_folder (Dict[str, List[str]]): Dictionary of files grouped by folder.
        repo_path (str): Path to the repository.

    Returns:
        Dict[str, Dict[str, str]]: Dictionary where keys are folder paths and values are dictionaries 
                                   with file names as keys and file contents as values.
    """
    content_by_folder = {}
    for folder, files in files_by_folder.items():
        folder_content = {}
        for file_name in files:
            # Construct the full file path
            file_path = os.path.join(repo_path, folder, file_name) if folder != "Root" else os.path.join(repo_path, file_name)
            try:
                # Ensure file exists before reading
                if not os.path.exists(file_path):
                    folder_content[file_name] = "File does not exist"
                    continue

                # Read the file content
                with open(file_path, "rb") as f:
                    raw_data = f.read()
                    # Detect encoding and decode content
                    detected_encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
                    content = raw_data.decode(detected_encoding, errors="ignore")  # Ignore decoding errors
                    folder_content[file_name] = content
            except Exception as e:
                folder_content[file_name] = f"Error reading file: {e}"
        content_by_folder[folder] = folder_content
    return content_by_folder




#Summarize content function
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
                        f"{content[:2000]}"  # Truncate to avoid exceeding token limits
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
    
    
    repo_path = "./clone_repo/dinov2_repo/dinov2"  # Change this to your repository's path

    # Step 1: List all files and folders (including all nested levels)
    files_by_folder = list_all_files_and_folders(repo_path)
    print("Files by folders:")
    for folder, files in files_by_folder.items():
        print(f"Folder: {folder}")
        for file in files:
            print(f"  - {file}")

    # Step 2: Read the content of all files
    print("\nStarting to read file contents...\n")
    content_by_folder = read_files_content(files_by_folder, repo_path)

    # Step 3: Summarize the content of files
    print("\nStarting to summarize file contents...\n")
    summaries_by_folder = summarize_content(content_by_folder)

    # Step 4: Display the summaries in an organized way
    for folder, summaries in summaries_by_folder.items():
        print(f"\nFolder: {folder}")
        for file_name, summary in summaries.items():
            print(f"  - File: {file_name}")
            print(f"    Summary:\n{summary}")
        print("\n" + "=" * 80 + "\n")
