# MCPVotsAGI Project Structure

## 📁 Directory Organization

This document outlines the professional organization of the MCPVotsAGI repository, designed for maximum clarity, maintainability, and ease of contribution.

### 🗂️ Root Directory

```
MCPVotsAGI/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CHANGELOG.md                 # Version history
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 SECURITY.md                  # Security policy
├── 📄 CODE_OF_CONDUCT.md          # Community guidelines
├── 📄 requirements.txt             # Python dependencies
├── 📄 package.json                 # Node.js dependencies
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .env.example                 # Environment variables template
└── 📄 docker-compose.yml           # Docker orchestration
```

### 🏗️ Source Code (`src/`)

#### **Core System (`src/core/`)**
```
src/core/
├── 📄 __init__.py
├── 📄 start_system_v2.py          # System startup orchestration
├── 📄 ecosystem_manager_v4_clean.py # Ecosystem management
├── 📄 launcher.py                  # Main application launcher
├── 📄 config.py                    # Global configuration
└── 📄 utils.py                     # Common utilities
```

#### **Trading System (`src/trading/`)**
```
src/trading/
├── 📄 __init__.py
├── 📄 unified_trading_backend_v2.py # Main trading backend
├── 📄 dgm_trading_algorithms_v2.py  # DGM algorithms
├── 📄 trading_strategies.py         # Strategy definitions
├── 📄 risk_management.py           # Risk management rules
└── 📄 portfolio_manager.py         # Portfolio management
```

#### **AI Integration (`src/ai/`)**
```
src/ai/
├── 📄 __init__.py
├── 📄 deepseek_integration.py      # DeepSeek-R1 integration
├── 📄 claude_integration.py        # Claude Code integration
├── 📄 gemini_integration.py        # Gemini integration
├── 📄 model_orchestrator.py        # Multi-AI orchestration
└── 📄 prompt_templates.py          # AI prompt templates
```

#### **Blockchain Integration (`src/blockchain/`)**
```
src/blockchain/
├── 📄 __init__.py
├── 📄 solana_integration_v2.py     # Solana blockchain
├── 📄 phantom_wallet.py            # Phantom wallet integration
├── 📄 defi_protocols.py            # DeFi integrations
├── 📄 zero_knowledge.py            # ZK proof implementation
└── 📄 jupiter_dex.py               # Jupiter DEX integration
```

#### **Monitoring System (`src/monitoring/`)**
```
src/monitoring/
├── 📄 __init__.py
├── 📄 health_checks.py             # System health monitoring
├── 📄 metrics_collector.py         # Prometheus metrics
├── 📄 performance_monitor.py       # Performance tracking
├── 📄 security_monitor.py          # Security monitoring
└── 📄 alerts.py                    # Alert system
```

#### **Testing Framework (`src/tests/`)**
```
src/tests/
├── 📄 __init__.py
├── 📄 test_framework_v2.py         # Main test framework
├── 📄 integration_tests.py         # Integration tests
├── 📄 performance_tests.py         # Performance benchmarks
├── 📄 mock_tests.py                # Mock service tests
├── 📄 stress_tests.py              # Load testing
└── 📄 fixtures/                    # Test fixtures
    ├── 📄 mock_data.py
    └── 📄 test_configs.py
```

### 📚 Documentation (`docs/`)

#### **API Documentation (`docs/api/`)**
```
docs/api/
├── 📄 README.md                    # API overview
├── 📄 trading_api.md               # Trading endpoints
├── 📄 blockchain_api.md            # Blockchain endpoints
├── 📄 monitoring_api.md            # Monitoring endpoints
├── 📄 ai_api.md                    # AI integration endpoints
└── 📄 webhooks.md                  # Webhook documentation
```

#### **Architecture (`docs/architecture/`)**
```
docs/architecture/
├── 📄 COMPREHENSIVE_SYSTEM_ANALYSIS.md # System analysis
├── 📄 system_overview.md           # High-level architecture
├── 📄 component_design.md          # Component specifications
├── 📄 data_flow.md                 # Data flow diagrams
├── 📄 security_architecture.md     # Security design
└── 📄 scalability_design.md        # Scaling strategies
```

#### **Deployment (`docs/deployment/`)**
```
docs/deployment/
├── 📄 quick_start.md               # Quick setup guide
├── 📄 production_setup.md          # Production deployment
├── 📄 docker_deployment.md         # Docker setup
├── 📄 cloud_deployment.md          # Cloud deployment
├── 📄 monitoring_setup.md          # Monitoring configuration
└── 📄 troubleshooting.md           # Common issues
```

#### **User Guide (`docs/user-guide/`)**
```
docs/user-guide/
├── 📄 getting_started.md           # User onboarding
├── 📄 trading_guide.md             # Trading features
├── 📄 ai_features.md               # AI capabilities
├── 📄 blockchain_guide.md          # Blockchain features
├── 📄 dashboard_guide.md           # Dashboard usage
└── 📄 faq.md                       # Frequently asked questions
```

### ⚙️ Configuration (`config/`)

#### **Development Configuration (`config/development/`)**
```
config/development/
├── 📄 ecosystem.yaml               # Dev ecosystem config
├── 📄 database.yaml                # Dev database config
├── 📄 ai_models.yaml               # Dev AI model config
└── 📄 logging.yaml                 # Dev logging config
```

#### **Production Configuration (`config/production/`)**
```
config/production/
├── 📄 ecosystem.yaml               # Prod ecosystem config
├── 📄 database.yaml                # Prod database config
├── 📄 security.yaml                # Security configuration
├── 📄 monitoring.yaml              # Monitoring config
└── 📄 scaling.yaml                 # Auto-scaling config
```

#### **Testing Configuration (`config/testing/`)**
```
config/testing/
├── 📄 test_ecosystem.yaml          # Test environment config
├── 📄 mock_services.yaml           # Mock service config
└── 📄 ci_config.yaml               # CI/CD configuration
```

### 🛠️ Scripts (`scripts/`)

#### **Setup Scripts (`scripts/setup/`)**
```
scripts/setup/
├── 📄 install_dependencies.py      # Dependency installation
├── 📄 setup_environment.py         # Environment setup
├── 📄 database_init.py             # Database initialization
├── 📄 START_PRODUCTION.bat         # Windows production start
├── 📄 START_DEVELOPMENT.bat        # Windows dev start
└── 📄 setup.sh                     # Unix setup script
```

#### **Deployment Scripts (`scripts/deployment/`)**
```
scripts/deployment/
├── 📄 deploy_production.py         # Production deployment
├── 📄 deploy_staging.py            # Staging deployment
├── 📄 rollback.py                  # Rollback script
├── 📄 health_check.py              # Deployment validation
└── 📄 backup_system.py             # System backup
```

#### **Maintenance Scripts (`scripts/maintenance/`)**
```
scripts/maintenance/
├── 📄 system_cleanup.py            # System cleanup
├── 📄 log_rotation.py              # Log management
├── 📄 performance_tune.py          # Performance tuning
├── 📄 security_audit.py            # Security auditing
└── 📄 database_maintenance.py      # Database maintenance
```

### 🐳 Containerization

```
├── 📄 Dockerfile                   # Main application container
├── 📄 docker-compose.yml           # Multi-service orchestration
├── 📄 docker-compose.dev.yml       # Development environment
├── 📄 docker-compose.prod.yml      # Production environment
└── 📁 docker/
    ├── 📄 api.Dockerfile           # API service container
    ├── 📄 worker.Dockerfile        # Background worker container
    └── 📄 nginx.Dockerfile         # Reverse proxy container
```

### 🔄 CI/CD (`.github/`)

```
.github/
├── 📁 workflows/
│   ├── 📄 ci.yml                   # Continuous integration
│   ├── 📄 cd.yml                   # Continuous deployment
│   ├── 📄 security.yml             # Security scanning
│   └── 📄 performance.yml          # Performance testing
├── 📁 ISSUE_TEMPLATE/
│   ├── 📄 bug_report.yml           # Bug report template
│   ├── 📄 feature_request.yml      # Feature request template
│   └── 📄 security_issue.yml       # Security issue template
└── 📁 PULL_REQUEST_TEMPLATE/
    └── 📄 pull_request_template.md # PR template
```

### 📊 Analytics & Monitoring

```
├── 📁 monitoring/
│   ├── 📄 prometheus.yml           # Prometheus configuration
│   ├── 📄 grafana_dashboards.json  # Grafana dashboards
│   └── 📄 alerts.yml               # Alert rules
└── 📁 analytics/
    ├── 📄 performance_metrics.py   # Performance analytics
    └── 📄 business_metrics.py      # Business intelligence
```

## 🎯 Key Organizational Principles

### 1. **Separation of Concerns**
- Each directory has a single, well-defined purpose
- Related functionality is grouped together
- Clear boundaries between different system layers

### 2. **Environment Isolation**
- Separate configurations for dev/staging/production
- Environment-specific scripts and settings
- Clear deployment strategies for each environment

### 3. **Comprehensive Documentation**
- Every major component is documented
- API documentation is complete and up-to-date
- Architecture decisions are recorded

### 4. **Testing Strategy**
- Unit tests alongside source code
- Integration tests in dedicated directory
- Performance and stress testing capabilities

### 5. **DevOps Integration**
- CI/CD pipelines for all environments
- Automated testing and deployment
- Infrastructure as code principles

### 6. **Security First**
- Security configurations separated by environment
- Security monitoring and auditing tools
- Secure secrets management

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/kabrony/mcpvotsagi.git
   cd mcpvotsagi
   ```

2. **Run setup script**
   ```bash
   # Windows
   scripts/setup/START_DEVELOPMENT.bat

   # Unix/Linux
   bash scripts/setup/setup.sh
   ```

3. **Follow environment-specific documentation**
   - Development: `docs/deployment/quick_start.md`
   - Production: `docs/deployment/production_setup.md`

## 📝 Contributing

Please read our [CONTRIBUTING.md](../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
