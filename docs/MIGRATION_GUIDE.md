# MCPVotsAGI Repository Migration Guide

## 🎯 Repository Enhancement Overview

Your MCPVotsAGI repository has been enhanced with a modern monorepo structure, advanced CI/CD pipelines, and production-ready configurations. This guide will help you complete the migration.

## 📋 Pre-Migration Checklist

Before running the migration scripts, ensure you have:

- [ ] **Node.js 20+** installed
- [ ] **PNPM 8+** installed (`npm install -g pnpm`)
- [ ] **Git** properly configured
- [ ] **Current code backed up** (script will create backup automatically)
- [ ] **Environment variables** documented

## 🚀 Migration Process

### Step 1: Run the Reorganization Script

```powershell
# Navigate to your project root
cd C:\Workspace\MCPVotsAGI

# Make scripts executable (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the reorganization script
.\scripts\reorganize-repo.ps1
```

### Step 2: Verify the Migration

```powershell
# Run the verification script
.\scripts\verify-migration.ps1
```

### Step 3: Install Dependencies

```powershell
# Install all dependencies using pnpm workspaces
pnpm install
```

### Step 4: Update Import Paths

The migration will move files to new locations. Update your import statements:

**Before:**
```typescript
import { Context7Integration } from '../core/CONTEXT7_INTEGRATION';
import { DeepSeekR1Agent } from '../agents/deepseek_agent';
```

**After:**
```typescript
import { Context7Integration } from '@mcpvotsagi/core';
import { DeepSeekR1Agent } from '@mcpvotsagi/agents';
```

### Step 5: Configure Environment Variables

Create environment files for each app:

```bash
# Root environment
cp .env.example .env.local

# Web app environment
cp apps/web/.env.example apps/web/.env.local

# API environment
cp apps/api/.env.example apps/api/.env.local
```

## 📁 New Directory Structure

```
mcpvotsagi/
├── apps/                          # Applications
│   ├── web/                      # Next.js frontend
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   ├── api/                      # Backend API
│   │   ├── src/
│   │   └── package.json
│   ├── agent-orchestrator/       # Agent coordination
│   └── mcp-server/              # MCP server
├── packages/                     # Shared packages
│   ├── core/                    # Core AGI engine
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── context7/
│   │   │   ├── deepseek/
│   │   │   └── oracle/
│   │   └── package.json
│   ├── agents/                  # AI agents
│   │   ├── src/
│   │   │   ├── context7/
│   │   │   ├── deepseek-r1/
│   │   │   └── oracle-claudia/
│   │   └── package.json
│   ├── strategies/              # Trading strategies
│   │   ├── src/
│   │   │   ├── arbitrage/
│   │   │   ├── momentum/
│   │   │   └── ml-based/
│   │   └── package.json
│   ├── blockchain/              # Blockchain integrations
│   │   ├── src/
│   │   │   ├── solana/
│   │   │   └── ethereum/
│   │   └── package.json
│   ├── ui/                      # Shared UI components
│   │   ├── src/
│   │   │   ├── components/
│   │   │   └── hooks/
│   │   └── package.json
│   └── types/                   # Shared TypeScript types
│       ├── src/
│       │   ├── agents.ts
│       │   ├── trading.ts
│       │   └── blockchain.ts
│       └── package.json
├── services/                    # Microservices
│   ├── price-feed/
│   ├── data-aggregator/
│   ├── risk-engine/
│   └── ml-inference/
├── infrastructure/              # Infrastructure as Code
│   ├── kubernetes/
│   ├── terraform/
│   ├── docker/
│   └── monitoring/
├── docs/                        # Documentation
│   ├── api/
│   ├── guides/
│   ├── architecture/
│   └── research/
├── scripts/                     # Development scripts
│   ├── setup/
│   ├── deploy/
│   └── migration/
├── tests/                       # Test suites
│   ├── integration/
│   ├── e2e/
│   └── performance/
├── .github/                     # GitHub workflows
│   └── workflows/
├── package.json                 # Root package.json
├── pnpm-workspace.yaml         # PNPM workspace config
├── turbo.json                  # Turbo build config
└── tsconfig.json               # TypeScript config
```

## 🔧 Development Commands

After migration, use these commands:

```bash
# Start all applications in development mode
pnpm dev

# Start specific application
pnpm dev --filter @mcpvotsagi/web
pnpm dev --filter @mcpvotsagi/api

# Build all packages
pnpm build

# Build specific package
pnpm build --filter @mcpvotsagi/core

# Run tests
pnpm test

# Run linting
pnpm lint

# Format code
pnpm format

# Type checking
pnpm typecheck

# Clean all build artifacts
pnpm clean
```

## 🔀 Git Workflow

The enhanced repository includes improved Git workflows:

```bash
# Feature development
git checkout -b feature/new-agent-integration
git add .
git commit -m "feat: add new agent integration"
git push origin feature/new-agent-integration

# Create pull request via GitHub UI
# After merge, the CI/CD pipeline will automatically:
# - Run tests
# - Build packages
# - Deploy to staging (if on develop branch)
# - Deploy to production (if on main branch)
```

## 🧪 Testing Strategy

The new structure supports comprehensive testing:

```bash
# Unit tests
pnpm test

# Integration tests
pnpm test:integration

# End-to-end tests
pnpm test:e2e

# Performance tests
pnpm test:performance

# Test coverage
pnpm test:coverage
```

## 📊 Monitoring & Observability

Enhanced monitoring capabilities:

- **Application Performance Monitoring (APM)**
- **Error tracking**
- **Metrics collection**
- **Log aggregation**
- **Alerting**

## 🚀 Deployment

### Staging Deployment
- Automatic deployment on `develop` branch
- Full integration testing environment
- Performance monitoring

### Production Deployment
- Automatic deployment on `main` branch
- Blue-green deployment strategy
- Rollback capabilities
- Health checks

## 🔒 Security

Enhanced security features:

- **Dependency scanning** with Snyk
- **Code quality checks** with SonarQube
- **Security linting** with ESLint security rules
- **Secrets management** with environment variables
- **Access control** with GitHub branch protection

## 📚 Documentation

The new structure includes comprehensive documentation:

- **API Documentation** - Auto-generated from code
- **Architecture Diagrams** - Visual system overview
- **Development Guides** - Step-by-step instructions
- **Research Notes** - AI/ML research and findings

## 🤝 Contributing

Enhanced contribution workflow:

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes with tests**
4. **Submit pull request**
5. **Automated CI/CD pipeline** runs
6. **Code review process**
7. **Merge and deployment**

## 📞 Support

If you encounter issues during migration:

1. Check the **troubleshooting section** below
2. Review **GitHub Issues** for similar problems
3. Create a **new issue** with detailed information
4. Join our **Discord community** for real-time support

## 🔧 Troubleshooting

### Common Issues

**Issue: PNPM not found**
```bash
# Solution: Install PNPM
npm install -g pnpm
```

**Issue: Permission denied on scripts**
```powershell
# Solution: Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue: Import path errors**
```typescript
// Solution: Update import paths
// Old: import { ... } from '../core/...'
// New: import { ... } from '@mcpvotsagi/core'
```

**Issue: Environment variables not found**
```bash
# Solution: Copy environment files
cp .env.example .env.local
```

## ✅ Post-Migration Checklist

- [ ] All tests passing
- [ ] All imports updated
- [ ] Environment variables configured
- [ ] CI/CD pipeline working
- [ ] Documentation updated
- [ ] Team members notified
- [ ] Deployment successful

## 🎉 What's Next?

After successful migration, you can:

1. **Develop new features** using the enhanced structure
2. **Scale your applications** with the microservices architecture
3. **Improve performance** with optimized build processes
4. **Enhance security** with automated scanning
5. **Expand internationally** with the robust foundation

---

**🚀 Your MCPVotsAGI repository is now ready for the next level of development!**
