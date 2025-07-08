# Contributing to MCPVotsAgi

Thank you for your interest in contributing to MCPVotsAgi! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- GitHub account

### Development Setup

1. **Fork the repository**
   ```bash
   gh repo fork kabrony/mcpvotsagi
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mcpvotsagi.git
   cd mcpvotsagi
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Run tests**
   ```bash
   python test_framework_v2.py
   ```

## 📋 Development Guidelines

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Follow ESLint configuration
- **Documentation**: Use Google-style docstrings
- **Commits**: Use conventional commit format

### Testing Requirements

- **Unit Tests**: Required for all new functions
- **Integration Tests**: Required for new components
- **Performance Tests**: Required for critical paths
- **Security Tests**: Required for auth/crypto code

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Run the test suite**
   ```bash
   python test_framework_v2.py
   npm test  # For frontend changes
   ```

4. **Commit your changes**
   ```bash
   git commit -m "feat: add your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Use the PR template
   - Link relevant issues
   - Request review from maintainers

## 🐛 Bug Reports

When filing bug reports, please include:

- **Environment**: OS, Python version, dependencies
- **Steps to reproduce**: Clear, numbered steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

## 💡 Feature Requests

For feature requests, please provide:

- **Problem statement**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought about
- **Additional context**: Mockups, examples, references

## 🔒 Security Issues

**DO NOT** file security issues in public GitHub issues. Instead:

1. Email: security@mcpvotsagi.com
2. Use GitHub Security Advisories
3. Provide detailed information about the vulnerability

## 📝 Documentation

### Types of Documentation

- **API Documentation**: In-code docstrings
- **Architecture Docs**: High-level system design
- **User Guides**: Step-by-step tutorials
- **Development Docs**: Setup and contribution guides

### Documentation Standards

- Use Markdown for all documentation
- Include code examples where applicable
- Keep documentation up-to-date with code changes
- Use clear, concise language

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Community input needed
- `priority:high`: Urgent issues
- `component:trading`: Trading system related
- `component:ai`: AI/ML related
- `component:blockchain`: Blockchain/Solana related

## 🎉 Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file
- Release notes
- Project documentation
- Annual contributor acknowledgments

## 📞 Getting Help

- **Discord**: [MCPVotsAgi Community](https://discord.gg/mcpvotsagi)
- **GitHub Discussions**: For questions and ideas
- **Documentation**: Check existing docs first
- **Issues**: For bugs and feature requests

## 📄 License

By contributing to MCPVotsAgi, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to MCPVotsAgi! 🚀
