
import ast
import os
from typing import List, Dict
from autogen import AssistantAgent

# Libraries to ignore
IGNORED_LIBRARIES = {
    "os", "sys", "argparse", "logging", "functools", "math", "json", "torch", "numpy", 
    "torch.nn", "torch.nn.parallel", "typing", "collections", "datetime", "time",
    "pathlib", "random", "enum", "copy", "warnings", "csv", "PIL", "io", "torchvision", "re", "socket"
}

config_list = [{
    "model": "llama3.1",
    "api_type": "ollama",
    "client_host": "http://localhost:11434",
    "timeout": 120,
    "cache_seed": None,
}]

# Define the summarization agent
summarization_agent = AssistantAgent(
    name="summarization_agent",
    system_message="Summarize the provided Python class, function, or module content and indicate whether it is related to a dataloader, training logic, model definition, evaluation, or utility function.",
    llm_config= {"config_list": config_list}
)

def extract_repo_imports(file_path: str) -> List[Dict[str, str]]:
    """
    Extract imported modules or classes/functions from a Python file.
    """
    imports = []
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        tree = ast.parse(source)

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] not in IGNORED_LIBRARIES:
                        imports.append({"type": "module", "name": alias.name})

            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] not in IGNORED_LIBRARIES:
                    for alias in node.names:
                        imports.append({"type": "symbol", "module": node.module, "name": alias.name})

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return imports

def resolve_import_path(import_item: Dict[str, str], repo_root: str) -> str:
    """
    Resolve the path of the imported module or symbol to a file.
    """
    if import_item["type"] == "module":
        module_path = os.path.join(repo_root, import_item["name"].replace('.', '/')) + '.py'
        if os.path.isfile(module_path) and module_path.startswith(repo_root):
            return module_path
    elif import_item["type"] == "symbol":
        base_path = os.path.join(repo_root, import_item["module"].replace('.', '/')) + '.py'
        if os.path.isfile(base_path) and base_path.startswith(repo_root):
            return base_path
    return None

def extract_class_or_function_content(file_path: str, symbol_name: str) -> str:
    """
    Extract the content of a specific class or function by its name.
    """
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        tree = ast.parse(source)

        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == symbol_name:
                return ast.unparse(node)  # Extract the full definition of the class or function
    except Exception as e:
        print(f"Error extracting content from {file_path}: {e}")
    return ""

def read_full_module_content(file_path: str) -> str:
    """
    Read the full content of a module file.
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading full module content from {file_path}: {e}")
    return ""

def summarize_content(class_or_function_contents: Dict[str, str]) -> Dict[str, str]:
    """
    Summarize the content of each class, function, or module using the summarization agent.
    """
    summaries = {}
    for item, content in class_or_function_contents.items():
        if content.strip():  # Skip empty content
            try:
                prompt = (
                    f"Summarize the content of the following Python class, function, or module and determine its category "
                    f"(dataloader, training logic, model definition, evaluation, utility function):\n\n"
                    f"{content[:2500]}"  # Truncate to avoid token overflow
                )
                response = summarization_agent.generate_reply(
                    messages=[{"role": "user", "content": prompt}]
                )

                if isinstance(response, dict) and "content" in response:
                    summaries[item] = response["content"]
                else:
                    summaries[item] = f"Unexpected response format: {response}"
            except Exception as e:
                summaries[item] = f"Error summarizing content: {str(e)}"
        else:
            summaries[item] = "No content found for this class, function, or module."
    return summaries

if __name__ == "__main__":
    repo_path = "/home/zohreh/workspace/my_project/clone_repo/dinov2/dinov2/logging"
    print(f"Scanning repository: {repo_path}")

    # Step 1: Walk through the repository and extract imports
    imports = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                imports[file_path] = extract_repo_imports(file_path)

    class_or_function_contents = {}  # Store content of imported classes/functions or full modules

    # Step 2: Resolve paths and extract specific content
    for py_file, import_list in imports.items():
        print(f"\nFile: {py_file}")
        print("Imports Found:", import_list)

        for import_item in import_list:
            resolved_path = resolve_import_path(import_item, repo_root=repo_path)
            if resolved_path:
                if import_item["type"] == "symbol":
                    # Extract content of specific class or function
                    content = extract_class_or_function_content(resolved_path, import_item["name"])
                    if content:
                        key = f"{resolved_path}::{import_item['name']}"
                        class_or_function_contents[key] = content
                elif import_item["type"] == "module":
                    # Read full module content
                    module_content = read_full_module_content(resolved_path)
                    if module_content:
                        key = f"{resolved_path} (full module)"
                        class_or_function_contents[key] = module_content

    # Step 3: Summarize the contents
    summaries = summarize_content(class_or_function_contents)

    # Display the summaries
    print("\nSummaries of the imported class, function, or module contents:")
    for item, summary in summaries.items():
        print(f"\n{item}")
        print(f"Summary:\n{summary}")



