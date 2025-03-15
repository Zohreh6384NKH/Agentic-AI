

import ast
import os
from pathlib import Path
import sys
from typing import List, Dict, Optional
from autogen import AssistantAgent





# Configuration for summarization agent
config_list = [{
    "model": "llama3.2",
    "api_type": "ollama",
    "client_host": "http://localhost:11434",
}]




llm_config = {
    "request_timeout": 600,
    "config_list": config_list,
    "temperature": 0,
    "seed": 43
}



# Define the summarization agent
summarization_agent = AssistantAgent(
    name="summarization_agent",
    system_message="Summarize the provided Python function or class in 4 sentences and categorize it into: "
                   "(train, configs, utils, dataloader, evaluation, model). "
                   "Return the category name in this format: CATEGORY: <category_name>.",
    llm_config=llm_config
)




# # Set project root and folder to scan
REPO_ROOT = Path("/home/zohreh/workspace/my_project/clone_repo/dinov2")
# FOLDER_TO_SCAN = REPO_ROOT / "dinov2"/"eval"/"depth"/"models"/"backbones"
FOLDER_TO_SCAN = REPO_ROOT / "dinov2"/"utils"
OUTPUT_DIR = REPO_ROOT / "categorized_code"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists



# # Mapping categories to filenames
CATEGORY_MAPPING = {
    "train": "train.py",
    "configs": "config.py",
    "utils": "utils.py",
    "dataloader": "dataloader.py",
    "evaluation": "eval.py",
    "model": "model.py"
}




# # Libraries to ignore
IGNORED_LIBRARIES = {
    "os", "sys", "argparse", "logging", "functools", "math", "json", "torch", "numpy",
    "torch.nn", "torch.nn.parallel", "typing", "collections", "datetime", "time",
    "pathlib", "random", "enum", "copy", "warnings", "csv", "PIL", "io", "torchvision", "re", "socket", "urllib.parse"
}


def extract_imports(file_path: Path, repo_root: Path) -> List[Dict[str, str]]:
    """Extract absolute and relative imports from a Python file."""
    imports = []
    try:
        source = file_path.read_text()
        tree = ast.parse(source)  # Parse the source code into an AST

        for node in ast.walk(tree):
            # Handle `import module`
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("dinov2"):
                        imports.append({"type": "module", "name": alias.name})

            # Handle `from module import symbol`
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] not in IGNORED_LIBRARIES:
                    resolved_module = node.module
                    if node.level > 0:
                        current_module_path = file_path.relative_to(repo_root).with_suffix("")
                        current_module_parts = list(current_module_path.parts)[:-1]
                        relative_module_parts = current_module_parts[: len(current_module_parts) - node.level + 1]
                        if node.module:
                            relative_module_parts.append(node.module)
                        resolved_module = ".".join(relative_module_parts)

                    for alias in node.names:
                        imports.append({"type": "symbol", "module": resolved_module, "name": alias.name, "level": node.level})
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return imports






def resolve_import_path(import_item: Dict[str, str], current_directory: Path, repo_root: Path) -> Optional[Path]:
    """Find the corresponding file or directory for an imported module or symbol, including absolute and relative imports."""
    
    module_name = import_item.get("name") if import_item["type"] == "module" else import_item.get("module")

    if not module_name:
        print(f"Skipping import due to missing module name: {import_item}")
        return None

    module_parts = module_name.split(".")

    #  Case 1: Absolute Imports (Modules starting with 'dinov2')
    if module_name.startswith("dinov2"):
        module_path = repo_root.joinpath(*module_parts)
        possible_paths = [
            module_path.with_suffix(".py"),  # Check if it's a standalone Python file
            module_path / "__init__.py"  # Check if it's a package with `__init__.py`
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Handle symbols (e.g., `from dinov2.logging import setup_logging`)
        if import_item["type"] == "symbol":
            name = import_item["name"]

            # Check if `name.py` exists in `module` directory
            direct_path = module_path / f"{name}.py"
            if direct_path.exists():
                return direct_path  # If the name exists as a Python file, return it

            # Search for the function/class `name` in all `.py` files inside the module directory
            if module_path.exists() and module_path.is_dir():
                for py_file in module_path.glob("*.py"):
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        if f"class {name}" in content or f"def {name}" in content:
                            return py_file  # Return the Python file containing the class/function

    #  Case 2: Relative Imports (`from .module import symbol`)
    if import_item.get("level", 0) > 0:
        relative_parts = module_name.lstrip(".").split(".")

        # Move up `level` directories from `current_directory`
        parent_directory = current_directory
        for _ in range(import_item["level"]):
            parent_directory = parent_directory.parent

        # Convert relative import to absolute path
        module_path = parent_directory.joinpath(*relative_parts)
        possible_paths = [
            module_path.with_suffix(".py"),
            module_path / "__init__.py"
        ]

        for path in possible_paths:
            if path.exists():
                return path

    #  Final Fallback: Return first available Python file in directory
    print(f"Could not resolve exact path for {import_item}. Extracting from available file.")
    for py_file in current_directory.glob("*.py"):
        return py_file  

    return None  # No valid file found

def extract_class_or_function_content(file_path: Path, symbol_name: str = None) -> str:
    """Extract the content of a specific imported class or function from a Python file."""
    try:
        source = file_path.read_text()
        tree = ast.parse(source)

        extracted_content = {}

        # Extract only the specific imported symbols
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and (not symbol_name or node.name == symbol_name):
                extracted_content[node.name] = ast.unparse(node)

        if symbol_name:
            return extracted_content.get(symbol_name, f"{symbol_name} not found in {file_path}")
        
        return "\n\n".join(extracted_content.values())

    except Exception as e:
        return f"Error extracting content from {file_path}: {e}"
    
    
    







# # # ### **Summarize and Categorize**
# # def summarize_content(class_or_function_contents: Dict[str, str]) -> Dict[str, str]:
# #     """Summarizes and categorizes extracted functions/classes using LLM."""
# #     categorized_imports = {}

# #     for name, content in class_or_function_contents.items():
# #         if not content.strip():
# #             continue

# #         try:
# #             prompt = (
# #                 f"Summarize the following Python function or class strictly in 4 sentences "
# #                 f"and determine its category: (train, configs, utils, dataloader, evaluation, model). "
# #                 f"Only return the category name in this format: CATEGORY: <category_name>.\n\n"
# #                 f"{content[:2500]}"
# #             )
# #             response = summarization_agent.generate_reply(messages=[{"role": "user", "content": prompt}])

# #             category = "utils"
# #             if isinstance(response, dict) and "content" in response:
# #                 for line in response["content"].split("\n"):
# #                     if line.strip().startswith("CATEGORY:"):
# #                         category = line.strip().split(":")[-1].strip().lower()
# #                         break

# #             category = category if category in CATEGORY_MAPPING else "utils"
# #             categorized_imports[name] = category
# #             print(f"Category : {category}")

# #         except Exception as e:
# #             print(f" Error categorizing content: {str(e)}")

# #     return categorized_imports




# # # ### **Save Extracted Source Code in Correct Files**
# # # def save_source_code(class_or_function_contents: Dict[str, str], categorized: Dict[str, str]):
# # #     """Saves extracted functions/classes into their corresponding categorized files."""
# # #     for name, category in categorized.items():
# # #         file_path = OUTPUT_DIR / CATEGORY_MAPPING[category]
# # #         with open(file_path, "a", encoding="utf-8") as f:
# # #             if class_or_function_contents[name].strip():  
# # #                 f.write(f"# {name} (Category: {category})\n{class_or_function_contents[name]}\n\n{'-'*80}\n\n")
                
                




#     # print(f"\n📂 Scanning repository: {FOLDER_TO_SCAN}")

#     # # Extract all imports from Python files
#     # imports = {file_path: extract_imports(file_path, REPO_ROOT) for file_path in FOLDER_TO_SCAN.rglob("*.py")}

#     # print(f"\n🔍 Extracted Imports: {imports}")

#     # # Dictionary to store extracted function/class contents
#     # extracted_contents = {}

#     # # Iterate through each Python file and its imports
#     # for py_file, import_list in imports.items():
#     #     for import_item in import_list:
#     #         resolved_path = resolve_import_path(import_item, py_file.parent)

#     #         print(f"\n📌 **Import:** `{import_item}`")
#     #         print(f"   ├── 🔗 Resolved Path: `{resolved_path}`")

#     #         if resolved_path:
#     #             symbol_name = import_item.get("name") if import_item["type"] == "symbol" else None
#     #             extracted_content = extract_class_or_function_content(resolved_path, symbol_name)

#     #             extracted_contents[import_item["name"] if symbol_name else str(resolved_path)] = {
#     #                 "resolved_path": resolved_path,
#     #                 "content": extracted_content
#     #             }

#     # # Print results
#     # print("\n" + "=" * 80)
#     # print("📜 Extracted Functions and Classes")
#     # print("=" * 80)

#     # for name, data in extracted_contents.items():
#     #     print(f"\n▶ **{name}**")
#     #     print(f"----------------------------")
#     #     print(f"📂 **Resolved Path:** `{data['resolved_path']}`")
#     #     print(f"\n```python\n{data['content']}\n```")
#     #     print("-" * 80)







if __name__ == "__main__":
    
    
    
    print(f"\nScanning repository: {FOLDER_TO_SCAN}")

    imports = {file_path: extract_imports(file_path, REPO_ROOT) for file_path in FOLDER_TO_SCAN.rglob("*.py")}
    print(f"Extracted Imports:\n{imports}\n{'='*50}")

    class_or_function_contents = {}
    for py_file, import_list in imports.items():
        for import_item in import_list:
            resolved_path = resolve_import_path(import_item, py_file.parent, REPO_ROOT)
            print(f"Import item: {import_item}, Resolved path: {resolved_path}")
            if resolved_path:
                if import_item["type"] == "symbol":
                    # Extract specific class or function content
                    content = extract_class_or_function_content(resolved_path, import_item["name"])
                    class_or_function_contents[import_item["name"]] = content
                    print(f"Extracted content for {import_item['name']}:\n{content}\n{'-'*50}")

                elif import_item["type"] == "module":
                    # Extract the entire content of the resolved module file
                    try:
                        content = resolved_path.read_text(encoding="utf-8")
                        class_or_function_contents[import_item["name"]] = content
                        print(f"Extracted full content of module {import_item['name']}:\n{content}...\n{'-'*50}")  # Print first 500 chars
                    except Exception as e:
                        print(f"Error reading module {import_item['name']} from {resolved_path}: {e}")

           






