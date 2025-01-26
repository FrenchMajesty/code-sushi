from code_sushi.core import File
from code_sushi.context import Context
import os
class LogicalChunk:
    """
    Represents a logical chunk of code. Often a function or method.
    """

    def __init__(self, context: Context, parent: File, name: str, code: str, absolute_path: str):
        self.context = context
        self.parent = parent
        self.name = name
        self.code = code
        self.absolute_path = absolute_path
        self.parent_summary = None

        common = os.path.commonprefix([context.output_dir, absolute_path])
        self.relative_path = absolute_path.replace(common, "", 1)
