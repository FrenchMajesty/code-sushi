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

        self.sanitize_relative_path(context.output_dir)

    def sanitize_relative_path(self, root: str):
        """
        Sanitize the relative path of the file.
        """
        common = os.path.commonprefix([root, self.absolute_path])
        self.relative_path = self.absolute_path.replace(common, "", 1)

        if self.relative_path.startswith("/"):
            self.relative_path = self.relative_path[1:]
