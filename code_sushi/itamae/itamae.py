import os
from tree_sitter import Parser, Tree
from .utils import extract_functions, init_parser, save_raw_function
from .logical_chunk import LogicalChunk
from code_sushi.core import File
from code_sushi.context import Context, LogLevel
from typing import Optional, List

class Itamae:
    """
    The Itamae is the module responsible for precisely slicing the code into logical chunks.
    """
    
    def slice_chunks(context: Context, file: File) -> List[LogicalChunk]:
        """Process the file to and extract every individual function."""
        
        parser = init_parser(file.extension)
        if not parser:
            return []
        
        code, syntax_tree = Itamae.parse_content(parser, file.absolute_path)
        functions = extract_functions(code, syntax_tree)

        # Parse each function into a logical chunk object
        chunks = []
        for func in functions:
            output_dir = context.output_dir + file.clean_path + ".functions/"
            file_path = save_raw_function(func, output_dir)

            if context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Saved: {file_path}")

            chunks.append(LogicalChunk(file, func["name"], func["code"], file_path))

        return chunks

    def parse_content(parser: Parser, file_path: str) -> tuple[str, Tree]:
        """Parse the content of the file and return the syntax tree."""

        code = open(file_path, "r", encoding="utf8").read()
        tree = parser.parse(bytes(code, "utf8"))
        return code, tree
