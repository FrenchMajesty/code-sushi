import os

def is_code_file(file: str) -> bool:
    """
    Check if the file is a code file.
    """
    code_file_extensions = set([
        # Python
        ".py", ".pyw", ".pyc", ".pyo", ".pyd",

        # JavaScript and TypeScript
        ".js", ".jsx", ".ts", ".tsx",

        # HTML and CSS
        ".html", ".htm", ".css",

        # C, C++, and C#
        ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".cs",

        # Java and Kotlin
        ".java", ".kt", ".kts",

        # Ruby
        ".rb",

        # PHP
        ".php",

        # Shell Scripts
        ".sh", ".bash", ".zsh",

        # Batch Scripts (Windows)
        ".bat", ".cmd",

        # Perl
        ".pl", ".pm",

        # Lua
        ".lua",

        # Rust
        ".rs",

        # Go
        ".go",

        # Swift
        ".swift",

        # SQL
        ".sql",

        # YAML and JSON
        ".yaml", ".yml", ".json",

        # Markdown (documentation often treated as code)
        ".md",

        # XML
        ".xml",

        # Docker and Infrastructure as Code
        ".dockerfile", ".tf", ".hcl",

        # Makefiles
        "Makefile",

        # Other config and scripts
        ".ini", ".cfg", ".toml",
    ])

    file_extension = os.path.splitext(file)[1]
    return file_extension in code_file_extensions
  