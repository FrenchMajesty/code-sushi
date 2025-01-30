import os
import hashlib

def save_raw_function(func, output_dir, ext):
    """Save an individual function into a file."""

    os.makedirs(output_dir, exist_ok=True)

    # Use function name or generate a unique name for anonymous functions
    random_hash = hashlib.sha256(func["code"].encode()).hexdigest()[:6]
    file_name = f"{func['name']}{ext}" if func["name"] != "anonymous" else f"anonymous_{random_hash}{ext}"
    file_name += ".md"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w") as f:
        f.write(func["code"])

    return file_path
