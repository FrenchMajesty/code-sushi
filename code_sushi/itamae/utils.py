from tree_sitter import Language, Parser, Tree
import tree_sitter_typescript as tstypescript
from code_sushi.core import File
from code_sushi.context import Context, LogLevel
from typing import List, Optional
import os
import hashlib

# Load supported languages
LANGUAGES = {
    ".ts": Language(tstypescript.language_typescript()),
    # Add more languages here if needed
}

def init_parser(extension: str) -> Optional[Parser]:
    """Initialize the parser for the given file extension. Return None if the extension is not supported."""

    language = LANGUAGES.get(extension)
    if not language:
        print(f"Skipping unsupported file: {extension}")
        return None

    parser = Parser()
    parser.set_language(language)
    return parser
    
def extract_functions(code: str, tree: Tree):
    """Extract all function/method definitions in the code."""
    root_node = tree.root_node
    functions = []

    # Traverse the syntax tree for function definitions
    def traverse(node):
        if node.type in {"function_declaration", "method_definition"}:  # Function and methods
            func_name_node = node.child_by_field_name("name")
            func_name = func_name_node.text.decode("utf8") if func_name_node else "anonymous"
            start_line, _ = node.start_point
            end_line, _ = node.end_point

            # Extract function code
            func_code = "\n".join(code.splitlines()[start_line:end_line + 1])
            functions.append({"name": func_name, "code": func_code})
        for child in node.children:
            traverse(child)

    traverse(root_node)
    return functions

def save_functions(context: Context, functions, output_dir: str):
    """Save each function into a separate file."""

    os.makedirs(output_dir, exist_ok=True)

    for func in functions:
        # Use function name or generate a unique name for anonymous functions
        file_name = f"{func['name']}.ts" if func["name"] != "anonymous" else f"anonymous_{functions.index(func)}.ts"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w") as f:
            f.write(func["code"])
        
        if context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Saved: {file_path}")

def save_raw_function(func, output_dir):
    """Save an individual function into a file."""

    os.makedirs(output_dir, exist_ok=True)

    # Use function name or generate a unique name for anonymous functions
    random_hash = hashlib.sha256(func["code"].encode()).hexdigest()[:6]
    file_name = f"{func['name']}.ts" if func["name"] != "anonymous" else f"anonymous_{random_hash}.ts"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w") as f:
        f.write(func["code"])

    return file_path
