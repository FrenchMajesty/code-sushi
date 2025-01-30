# Code Sushi 🍣

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
[![PyPI version](https://badge.fury.io/py/code-sushi.svg)](https://badge.fury.io/py/code-sushi)
[![Stars](https://img.shields.io/github/stars/frenchmajesty/code-sushi?style=social.svg)](https://github.com/frenchmajesty/code-sushi)


**Code Sushi** is a tool to help developers take large repos and cut them down into bite-sized pieces that can be fed into an LLM for answering questions in a few minutes.

## 🌟 Features
  
✅ **Multi-Language Support** – Can work with any programming language. (currently only Python, Typescript, and PHP is supported)
✅ **Privacy-First** – All code processing happens locally in the CLI tool. Your code never leaves your machine.  
✅ **Modular Components** – Easily swap out LLM, vector DB, and embedding providers with your preferred choices.

## 🧑‍🤝‍🧑 Who is this for?

- You work in a company that has very strict data privacy policies, operates in a regulated industry, or you are just paranoid about your code.
-> If not, [Cursor](https://www.cursor.com) is an excellent choice.

- You are dealing with a very large codebase (+50k lines of code) that cannot fit into the context window.
-> If not, I recommend [Gitingest](https://github.com/cyclotruc/gitingest) as an alternative.

- You just want question-answering capabilities for your codebases.
-> If you need much such as code completion, etc... there are no open-source IDEs that can do that yet. At least I haven't found any. If you do, please let me know and I'll update this section.

## 📦 Installation

You just need to have Python `3.12` or higher.
```sh
pip install code-sushi
```

## 🚀 Quick Start

Here is how you can use Code Sushi locally.

```sh
sushi init # Will create a .sushiignore file in your project root
sushi run # Will start the process of cutting down your repo.
```

Before the process starts, the tool will show a summary of the files detected and ask you to confirm the process.

## 📖 Usage

### **Basic Commands**

```sh
sushi init          # Creates a .sushiignore file in your project root
sushi slice         # Will start the process of cutting down your repo into smaller pieces
sushi upload        # Will upload the files to a Blob Storage
sushi vectorize     # Will embed the summaries and vectorize them for every file and chunk in disk
sushi clean         # Will clean up the .llm/ folder where the summaries are stored

sushi run           # Will run the entire process to slice and vectorize your repo in one command

sushi chat          # Will start a chat with the LLM
sushi ask           # Will ask a single question to the LLM
```

You can run the commands with the `-h` flag to get more information about the parameters each command accepts.

### **Configuration** TODO:
The `sushi init` command automatically creates a `sushi-config.json` file in your project root:
```json
{
    "max_agents": 10,
    "blog_storage_max_concurrent_requests": 25,
    "embedding_max_chunk_size": 128,
    "vector_db_max_concurrent_requests": 25
}
```

## 🔍 Inner Workings

Code Sushi uses a combination of AI services for each part of its workflow to understand and classify your code effectively:

- We use [Together.ai](https://together.ai) to access Llama 3.3 70B for understanding the code and answering questions.
- We use [Voyage.ai](https://voyageai.com) for creating embeddings and reranking search results.
- We use [Pinecone](https://pinecone.io) to store the vector embeddings and search against them for RAG.

### 🔄 Modular Architecture
Each component is designed to be easily swappable. If you desire to do so, you can implement your own LLM provider, vector database, and more. 

My only ask: I would kindly ask you to contribute your changes back to the project so that others can benefit from your work instead of a fork. 😇

## 📝 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements
- Thank you to [Romain](https://github.com/cyclotruc) for the initial inspiration with his [gitingest](https://github.com/cyclotruc/gitingest) project.

## 👥 Contributors

Want to be part of building Code Sushi? Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started! We always welcome contributions to improve the tool for benefit of the community.

---

**Made with ❤️ and many 🍣. - The Code Sushi team!**
