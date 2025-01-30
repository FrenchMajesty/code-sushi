# Code Sushi 🍣

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

**Code Sushi** is an simple open source tool to help developers take large repos and cut them down into bite-sized pieces that can be fed into an LLM for question answering.

---

## 🌟 Features

✅ **Natural Language Editing** – Simply describe the changes you want to make in plain English.  
✅ **Multi-Language Support** – Works with any programming language.  
✅ **Context-Aware** – Understands your code structure and makes targeted changes.  
✅ **Version Control Friendly** – Git-compatible changes.  
✅ **IDE Integration** – Seamlessly works with popular IDEs and text editors.  


## 🚀 Getting Started

### **Prerequisites**
- **Python 3.12 or higher**


## 🛠 Installation

Using pip:
```sh
pip install code-sushi
```


## ⚡ Quick Start

### Initialize Code Sushi in your project:
```sh
sushi init
```

### Start making changes:
```sh
sushi run
```

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

## 🎯 Examples

🔹 **Add input validation**:
```sh
code-sushi edit "Add input validation to the user registration function"
```

🔹 **Refactor for performance**:
```sh
code-sushi edit "Optimize the database query in users.service.ts"
```

🔹 **Add documentation**:
```sh
code-sushi edit "Add JSDoc comments to the authentication middleware"
```

## 🤝 Contributing

We love contributions! Please follow these steps to contribute:

1. **Fork** the repository  
2. Create your feature branch:  
```sh
git checkout -b feature/AmazingFeature
```
3. **Commit your changes**:  
```sh
git commit -m "Add some AmazingFeature"
```
4. **Push to the branch**:  
```sh
git push origin feature/AmazingFeature
```
5. **Open a Pull Request** 🚀  


## 📝 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.


## 🙏 Acknowledgments

🎉 Thanks to all our contributors!  
💡 Inspired by modern developer workflows.  
❤️ Built with passion for developers.  


## 📫 Support

📖 **Documentation**: [docs.codesushi.dev](#)  
🐞 **Issues**: [GitHub Issues](#)  
💬 **Discord**: [Join our community](#)  
🐦 **Twitter**: [@CodeSushi](#)  

## 👥 Contributors

<a href="https://github.com/code-sushi/code-sushi/graphs/contributors">
<img src="https://contrib.rocks/image?repo=code-sushi/code-sushi" />
</a>

Want to be part of building Code Sushi? Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started!

### Special Thanks To:

- All our amazing contributors who help make Code Sushi better
- The open source community for inspiration and support
- Our early adopters and testers who provided valuable feedback

---

**Made with 🍣 by the Code Sushi team!**
