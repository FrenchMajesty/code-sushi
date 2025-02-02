from setuptools import setup, find_packages

setup(
    name="code-sushi",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if needed
    entry_points={
        "console_scripts": [
            "sushi=code_sushi.main:main",  # Expose the `main` function as the CLI entry
        ]
    },
)
