from code_sushi.core import File
from code_sushi.context import Context, LogLevel
from typing import List, Optional
from code_sushi.itamae.code_fragment import CodeFragment
from tree_sitter import Parser, Language, Tree
import tree_sitter_typescript as tstypescript
import tree_sitter_javascript as tsjavascript
import tree_sitter_php as tsphp
import tree_sitter_python as tspython
import hashlib

LANGUAGES = {
    ".ts": Language(tstypescript.language_typescript()),
    ".tsx": Language(tstypescript.language_tsx()),
    ".js": Language(tsjavascript.language()),
    ".py": Language(tspython.language()),
    ".php": Language(tsphp.language_php()),
    # Add more languages here if needed
}


class TreeProcessor:
    def __init__(self, context: Context, file: File):
        self.context = context
        self.file = file

        self.parser = self._init_parser()

    def _init_parser(self) -> Optional[Parser]:
        """
        Initialize the parser for the given file. Return None if the extension is not supported.
        """
        try:
            language = LANGUAGES.get(self.file.ext, None)
            if not language:
                if self.context.is_log_level(LogLevel.DEBUG):
                    print(f"Itamae cannot slice unsupported file: {self.file.ext}. Skipping...")
                return None

            return Parser(language)
        except Exception as e:
            print(f"Error in TreeProcessor.init_parser(): {e}")
            return None

    def is_supported(self) -> bool:
        """
        Check if the file can be processed by this processor.
        """
        return self.parser is not None

    def extract(self) -> List[CodeFragment]:
        """
        Parse the content of the file and return a list of LogicalChunks.
        """
        code, syntax_tree = self._parse_content(self.file.absolute_path)
        functions = self._extract_functions(code, syntax_tree)
        return functions

    def _parse_content(self, path: str) -> tuple[str, Tree]:
        """
        Parse the content of the file and return a tuple with the code and the syntax tree.
        """
        code = open(path, "r", encoding="utf8").read()
        syntax_tree = self.parser.parse(bytes(code, "utf8"))
        return code, syntax_tree

    def _extract_functions(self, code: str, tree: Tree) -> List[CodeFragment]:
        """
        Extract all function/method definitions in the code.
        """
        root_node = tree.root_node
        functions = []

        # Traverse the syntax tree for function definitions
        def traverse(node):
            valid_types = set(["function_declaration", "method_definition", "method_declaration"])
            if node.type in valid_types:
                func_name_node = node.child_by_field_name("name")
                func_name = func_name_node.text.decode("utf8") if func_name_node else "anonymous"
                start_line, _ = node.start_point
                end_line, _ = node.end_point

                if func_name == "anonymous":
                    random_hash = hashlib.sha256(code.encode()).hexdigest()[:6]
                    func_name = f"anonymous_{random_hash}"

                fragment = CodeFragment(
                    path=self.file.absolute_path,
                    name=func_name,
                    content=code,
                    start_line=start_line,
                    end_line=end_line,
                )
                functions.append(fragment)
            
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return functions
