# 🚀 MCPVotsAgi Development Guide

## Quick Start

### 1. **One-Command Setup**
```bash
# Clone and setup in one command
git clone https://github.com/kabrony/mcpvotsagi.git
cd mcpvotsagi
python setup.py
```

### 2. **Environment Configuration**
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. **Start Development**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Start the system
python src/core/launcher.py
```

## 🏗️ Development Workflow

### Project Structure
```
MCPVotsAgi/
├── 📁 src/                    # Source code
│   ├── core/                  # Core system components
│   ├── trading/               # Trading algorithms
│   ├── ai/                    # AI model integrations
│   ├── blockchain/            # Blockchain integration
│   ├── monitoring/            # System monitoring
│   └── tests/                 # Test suite
├── 📁 docs/                   # Documentation
├── 📁 scripts/                # Automation scripts
├── 📁 config/                 # Configuration files
└── 📁 .github/                # GitHub workflows
```

### Development Commands

#### **Setup & Installation**
```bash
# Full setup with dependencies
python setup.py

# Skip dependency installation
python setup.py --skip-deps

# Verbose setup
python setup.py --verbose
```

#### **Testing**
```bash
# Run all tests
python -m pytest src/tests/

# Run specific test categories
python -m pytest src/tests/integration_tests.py
python -m pytest src/tests/performance_tests.py

# Run with coverage
python -m pytest --cov=src src/tests/
```

#### **Code Quality**
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
pylint src/

# Type checking
mypy src/
```

#### **Security**
```bash
# Security scan
bandit -r src/
safety check

# Dependency vulnerabilities
pip-audit
```

## 🔧 Development Tools

### **Required Tools**
- **Python 3.8+**: Core runtime
- **Git**: Version control
- **Node.js 18+**: Frontend dependencies
- **Docker**: Containerization (optional)

### **Recommended IDE Setup**

#### **VS Code Extensions**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "ms-toolsai.jupyter",
    "redhat.vscode-yaml",
    "ms-vscode.vscode-json",
    "github.copilot"
  ]
}
```

#### **Settings**
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### **PyCharm Setup**
1. Open project in PyCharm
2. Configure interpreter: `Settings > Project > Python Interpreter`
3. Set interpreter to `./venv/bin/python`
4. Enable code formatting: `Settings > Tools > Actions on Save`

## 🧪 Testing Strategy

### **Test Categories**
- **Unit Tests**: Individual function testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Speed and memory benchmarks
- **Security Tests**: Vulnerability scanning
- **End-to-End Tests**: Full system workflow testing

### **Test Configuration**
```python
# pytest.ini
[tool:pytest]
testpaths = src/tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

### **Mock Testing**
```python
# Use mocks for external services
@pytest.fixture
def mock_trading_api():
    with patch('src.trading.api.TradingClient') as mock:
        yield mock

def test_trading_strategy(mock_trading_api):
    # Test trading logic without real API calls
    pass
```

## 🚀 Deployment

### **Local Development**
```bash
# Start all services
python src/core/launcher.py

# Start specific service
python src/core/launcher.py --service=trading

# Development mode with hot reload
python src/core/launcher.py --dev
```

### **Docker Development**
```bash
# Build and run
docker-compose up --build

# Run specific service
docker-compose up mcpvots-core

# View logs
docker-compose logs -f mcpvots-core
```

### **Production Deployment**
```bash
# Build for production
docker build -t mcpvotsagi:latest .

# Deploy with compose
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring & Debugging

### **Logging**
```python
import logging
logger = logging.getLogger(__name__)

# Log levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### **Health Checks**
```bash
# Check system health
curl http://localhost:8090/health

# Check specific service
curl http://localhost:8090/health/trading
```

### **Performance Profiling**
```python
# Profile code performance
import cProfile
import pstats

# Profile a function
cProfile.run('your_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

## 🔐 Security Guidelines

### **API Key Management**
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate keys regularly
- Use different keys for different environments

### **Code Security**
```bash
# Scan for security issues
bandit -r src/

# Check dependencies for vulnerabilities
safety check
pip-audit
```

### **Git Security**
```bash
# Check for secrets before commit
git diff --cached | grep -i "api_key\|password\|secret"

# Use git-secrets
git secrets --scan
```

## 🤝 Contributing

### **Development Process**
1. **Fork** the repository
2. **Create** a feature branch
3. **Write** tests for new functionality
4. **Ensure** all tests pass
5. **Submit** a pull request

### **Code Standards**
- Follow PEP 8 style guide
- Write comprehensive docstrings
- Include type hints
- Write tests for new features
- Keep functions small and focused

### **Commit Messages**
```
feat: add new trading algorithm
fix: resolve memory leak in data collector
docs: update API documentation
test: add unit tests for blockchain integration
refactor: optimize database queries
```

## 📚 Learning Resources

### **Architecture Understanding**
- Read `docs/architecture/SYSTEM_ARCHITECTURE.md`
- Review `COMPREHENSIVE_SYSTEM_ANALYSIS.md`
- Study component interaction diagrams

### **Trading Concepts**
- Algorithmic trading fundamentals
- Risk management principles
- Market data analysis
- Portfolio optimization

### **AI Integration**
- Multi-model orchestration
- Prompt engineering
- Context management
- Performance optimization

### **Blockchain Development**
- Solana programming model
- DeFi protocols
- Wallet integration
- Transaction handling

## 🔧 Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```bash
# Find process using port
lsof -i :8090  # Linux/Mac
netstat -ano | findstr :8090  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /F /PID <PID>  # Windows
```

#### **Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **Database Connection Issues**
```bash
# Check database files
ls -la data/
# Reset database
rm data/*.db
python src/core/launcher.py --init-db
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python src/core/launcher.py

# Enable development mode
export ENVIRONMENT=development
python src/core/launcher.py --dev
```

## 📞 Support

### **Getting Help**
- **Documentation**: Check `docs/` directory
- **Issues**: Create GitHub issue
- **Discussions**: Use GitHub discussions
- **Security**: Email security@mcpvotsagi.com

### **Issue Templates**
- **Bug Report**: Use bug report template
- **Feature Request**: Use feature request template
- **Performance Issue**: Include profiling data
- **Security Issue**: Follow security policy

---

**Happy coding! 🚀**

*This development guide is continuously updated. Check back regularly for new features and improvements.*
