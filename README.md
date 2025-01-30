# Code Sushi 🍣

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

**Code Sushi** is an simple open source tool to help developers take large repos and cut them down into bite-sized pieces that can be fed into an LLM for question answering.

## 🌟 Features

✅ **Natural Language Editing** – Simply describe the changes you want to make in plain English.  
✅ **Multi-Language Support** – Can work with any programming language. (currently only Python, Typescript, and PHP is supported)
✅ **Context-Aware** – Understands your code structure and makes targeted changes.  
✅ **Version Control Friendly** – Git-compatible changes.  
✅ **IDE Integration** – Seamlessly works with popular IDEs and text editors.  


## 📦 Installation

You just need to have Python `3.12` or higher installed.
Using pip:
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
code-sushi edit "<instruction>"   # Make changes based on a natural language instruction
code-sushi review                 # Review pending changes
code-sushi apply                  # Apply suggested changes
code-sushi undo                   # Undo the last change
```

### **Configuration**
Create a `code-sushi.config.js` file in your project root:
```js
module.exports = {
language: 'auto',
style: 'standard',
safeMode: true,
// Add more configuration options
};
```

## 🔍 Inner Workings

Code Sushi uses a combination of powerful AI services to understand and modify your code effectively:

- Uses [Together.ai](https://together.ai) to access Llama 3.3 70B for understanding the code and answering questions.
- Uses [Voyage.ai](https://voyageai.com) for creating embeddings and reranking search results.
- Uses [Pinecone](https://pinecone.io) to store the vector embeddings and search against them for RAG.

### 🔄 Modular Architecture
Each component is designed to be easily swappable. If you desire to do so, you can implement your own LLM provider, vector database, and more. I would kindly ask you to contribute your changes back to the project so that others can benefit from your work instead of a fork. 😇

## 📝 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements
- Thank you to [Romain](https://github.com/cyclotruc) for the initial inspiration with his [gitingest](https://github.com/cyclotruc/gitingest) project.

## 👥 Contributors

<a href="https://github.com/code-sushi/code-sushi/graphs/contributors">
<img src="https://contrib.rocks/image?repo=code-sushi/code-sushi" />
</a>

Want to be part of building Code Sushi? Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started! We always welcome contributions to improve the tool for benefit of the community.

---

**Made with ❤️ and many 🍣. - The Code Sushi team!**
