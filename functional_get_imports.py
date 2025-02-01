# import ast
# from typing import List, Set
# import os

# IGNORED_LIBRARIES = {
#     "os", "sys", "argparse", "logging", "functools", "math", "json", "torch", "numpy", 
#     "torch.nn", "torch.nn.parallel", "typing"
# }

# def extract_repo_imports(file_path: str, repo_root: str) -> List[str]:
#     """
#     Extract imported modules or functions/classes from a Python file that belong to the project repository.
#     Excludes external libraries and Python standard libraries.

#     Args:
#         file_path (str): Path to the Python file to analyze.
#         repo_root (str): Root directory of the repository.

#     Returns:
#         List[str]: List of imported modules, classes, or functions within the repository.
#     """
#     imports = set()

#     try:
#         with open(file_path, 'r') as f:
#             source = f.read()
#         tree = ast.parse(source)

#         for node in tree.body:
#             # Handle `import module_name` statements
#             if isinstance(node, ast.Import):
#                 for alias in node.names:
#                     module_name = alias.name.split('.')[0]  # Get top-level module
#                     if module_name not in IGNORED_LIBRARIES:
#                         # Check if the module exists within the repo
#                         module_path = os.path.join(repo_root, module_name.replace('.', '/'))
#                         if os.path.isdir(module_path) or os.path.isfile(module_path + ".py"):
#                             imports.add(module_name)

# #             # Handle `from module import ...` statements
#             elif isinstance(node, ast.ImportFrom):
#                 if node.module and node.module.split('.')[0] not in IGNORED_LIBRARIES:
#                     # Check if the base module is within the repository
#                     module_path = os.path.join(repo_root, node.module.replace('.', '/'))
#                     if os.path.isdir(module_path) or os.path.isfile(module_path + ".py"):
#                         # Collect the imported names (e.g., functions or classes)
#                         for alias in node.names:
#                             imports.add(alias.name)

#     except Exception as e:
#         print(f"Error processing {file_path}: {e}")

#     return sorted(list(imports))  # Return sorted unique imports


# # Example usage
# if __name__ == "__main__":
#     file_path = "/home/zohreh/workspace/my_project/clone_repo/dinov2_repo/dinov2/dinov2/train/ssl_meta_arch.py"
#     repo_path = "/home/zohreh/workspace/my_project/clone_repo/dinov2_repo/dinov2"

#     result = extract_repo_imports(file_path, repo_path)
#     print("Internal imports found:", result)




import ast
import os
from typing import List, Set

IGNORED_LIBRARIES = {
    "os", "sys", "argparse", "logging", "functools", "math", "json", "torch", "numpy", 
    "torch.nn", "torch.nn.parallel", "typing"
}

def extract_repo_imports(file_path: str, repo_root: str) -> List[str]:
    """
    Extract imported modules or functions/classes from a Python file that belong to the project repository.
    Excludes external libraries and Python standard libraries.

    Args:
        file_path (str): Path to the Python file to analyze.
        repo_root (str): Root directory of the repository.

    Returns:
        List[str]: List of imported modules, classes, or functions within the repository.
    """
    imports = set()

    try:
        with open(file_path, 'r') as f:
            source = f.read()
        tree = ast.parse(source)

        for node in tree.body:
            # Handle `import module_name` statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]  # Get top-level module
                    if module_name not in IGNORED_LIBRARIES:
                        # Check if the module exists within the repo
                        module_path = os.path.join(repo_root, module_name.replace('.', '/'))
                        if os.path.isdir(module_path) or os.path.isfile(module_path + ".py"):
                            imports.add(module_name)

            # Handle `from module import ...` statements
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] not in IGNORED_LIBRARIES:
                    # Check if the base module is within the repository
                    module_path = os.path.join(repo_root, node.module.replace('.', '/'))
                    if os.path.isdir(module_path) or os.path.isfile(module_path + ".py"):
                        # Collect the imported names (e.g., functions or classes)
                        for alias in node.names:
                            imports.add(alias.name)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return sorted(list(imports))  # Return sorted unique imports


def walk_and_extract_imports(repo_root: str) -> dict:
    """
    Walk through the entire repository and extract internal imports from each Python file.

    Args:
        repo_root (str): Root directory of the repository.

    Returns:
        dict: Dictionary where keys are file paths and values are lists of internal imports.
    """
    all_imports = {}

    for root, _, files in os.walk(repo_root):
        for file in files:
            if file.endswith(".py"):  # Process only Python files
                file_path = os.path.join(root, file)
                imports = extract_repo_imports(file_path, repo_root)
                if imports:  # Only add files with internal imports
                    all_imports[file_path] = imports

    return all_imports


if __name__ == "__main__":
    repo_path = "/home/zohreh/workspace/my_project/clone_repo/dinov2_repo/dinov2"

    # Walk through the repository and extract internal imports
    result = walk_and_extract_imports(repo_path)

    # Print the internal imports for each file
    for file_path, imports in result.items():
        print(f"\nFile: {file_path}")
        print("Internal imports found:", imports)


