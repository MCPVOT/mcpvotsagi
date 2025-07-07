# MCPVotsAGI Repository Reorganization Script (PowerShell)
# This script will reorganize your repository into a modern monorepo structure

Write-Host "🚀 Starting MCPVotsAGI repository reorganization..." -ForegroundColor Green

# Create backup
$backupName = "mcpvotsagi-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host "📦 Creating backup: $backupName" -ForegroundColor Yellow
Copy-Item -Path "." -Destination "../$backupName" -Recurse -Force

# Create new directory structure
Write-Host "📁 Creating enhanced directory structure..." -ForegroundColor Blue

$directories = @(
    ".github/workflows",
    ".github/ISSUE_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE",
    "apps/web",
    "apps/api",
    "apps/agent-orchestrator",
    "apps/mcp-server",
    "packages/core/src",
    "packages/agents/src",
    "packages/strategies/src",
    "packages/blockchain/src",
    "packages/ui/src",
    "packages/types/src",
    "packages/config/src",
    "packages/utils/src",
    "services/price-feed",
    "services/data-aggregator",
    "services/risk-engine",
    "services/ml-inference",
    "infrastructure/kubernetes",
    "infrastructure/terraform",
    "infrastructure/docker",
    "infrastructure/monitoring",
    "contracts/solana",
    "contracts/ethereum",
    "data/models",
    "data/datasets",
    "data/configs",
    "docs/api",
    "docs/guides",
    "docs/architecture",
    "docs/research",
    "docs/diagrams",
    "docs/assets",
    "scripts/setup",
    "scripts/deploy",
    "scripts/analysis",
    "scripts/migration",
    "tests/integration",
    "tests/e2e",
    "tests/performance",
    "tests/chaos",
    ".vscode",
    ".husky",
    "config"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created: $dir" -ForegroundColor Green
    }
}

# Move existing files to new locations
Write-Host "📂 Reorganizing existing files..." -ForegroundColor Yellow

# Move core files
if (Test-Path "src/core") {
    Write-Host "Moving core files to packages/core..." -ForegroundColor Cyan
    Get-ChildItem "src/core" | Move-Item -Destination "packages/core/src" -Force
}

# Move agent files
if (Test-Path "src/agents") {
    Write-Host "Moving agent files to packages/agents..." -ForegroundColor Cyan
    Get-ChildItem "src/agents" | Move-Item -Destination "packages/agents/src" -Force
}

# Move trading files
if (Test-Path "src/trading") {
    Write-Host "Moving trading files to packages/strategies..." -ForegroundColor Cyan
    Get-ChildItem "src/trading" | Move-Item -Destination "packages/strategies/src" -Force
}

# Move blockchain files
if (Test-Path "src/blockchain") {
    Write-Host "Moving blockchain files to packages/blockchain..." -ForegroundColor Cyan
    Get-ChildItem "src/blockchain" | Move-Item -Destination "packages/blockchain/src" -Force
}

# Move frontend files
if (Test-Path "frontend") {
    Write-Host "Moving frontend to apps/web..." -ForegroundColor Cyan
    Get-ChildItem "frontend" | Move-Item -Destination "apps/web" -Force
    Remove-Item "frontend" -Recurse -Force
}

# Create configuration files
Write-Host "📝 Creating configuration files..." -ForegroundColor Blue

# Root package.json
$rootPackageJson = @"
{
  "name": "mcpvotsagi",
  "version": "3.0.0",
  "private": true,
  "description": "The ULTIMATE AGI System V3 - MCP-based AGI for Solana DEX trading",
  "author": "kabrony",
  "license": "MIT",
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=8.0.0"
  },
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "start": "turbo start",
    "lint": "turbo lint",
    "test": "turbo test",
    "typecheck": "turbo typecheck",
    "clean": "turbo clean && Remove-Item -Recurse -Force node_modules",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,md,yml,yaml}\"",
    "prepare": "husky install",
    "analyze": "turbo run analyze",
    "deploy:staging": "turbo run deploy:staging",
    "deploy:production": "turbo run deploy:production"
  },
  "devDependencies": {
    "@changesets/cli": "^2.27.1",
    "@commitlint/cli": "^18.4.4",
    "@commitlint/config-conventional": "^18.4.4",
    "eslint": "^8.56.0",
    "husky": "^8.0.3",
    "lint-staged": "^15.2.0",
    "prettier": "^3.2.4",
    "turbo": "^1.11.3",
    "typescript": "^5.3.3"
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ]
  }
}
"@

Set-Content -Path "package.json" -Value $rootPackageJson

# pnpm-workspace.yaml
$pnpmWorkspace = @"
packages:
  - "apps/*"
  - "packages/*"
  - "services/*"
  - "contracts/*"
"@

Set-Content -Path "pnpm-workspace.yaml" -Value $pnpmWorkspace

# turbo.json
$turboConfig = @"
{
  "`$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**", "build/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "outputs": [],
      "dependsOn": ["^build"]
    },
    "typecheck": {
      "outputs": [],
      "dependsOn": ["^build"]
    },
    "test": {
      "outputs": ["coverage/**"],
      "dependsOn": ["^build"]
    },
    "analyze": {
      "outputs": ["analysis/**"],
      "dependsOn": ["build"]
    },
    "deploy:staging": {
      "dependsOn": ["build", "test"],
      "cache": false
    },
    "deploy:production": {
      "dependsOn": ["build", "test"],
      "cache": false
    },
    "clean": {
      "cache": false
    }
  }
}
"@

Set-Content -Path "turbo.json" -Value $turboConfig

# .gitignore
$gitignore = @"
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/
*.lcov
.nyc_output

# Production
dist/
build/
.next/
out/

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
!.vscode/launch.json
!.vscode/tasks.json
.idea/
*.swp
*.swo
.DS_Store

# Turbo
.turbo/

# Vercel
.vercel/

# TypeScript
*.tsbuildinfo

# Temporary
tmp/
temp/
"@

Set-Content -Path ".gitignore" -Value $gitignore

# VSCode settings
$vscodeSettings = @"
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "eslint.workingDirectories": [
    { "mode": "auto" }
  ],
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/.next": true,
    "**/coverage": true
  }
}
"@

Set-Content -Path ".vscode/settings.json" -Value $vscodeSettings

Write-Host "✅ Repository reorganization complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Review the new structure" -ForegroundColor White
Write-Host "2. Run 'pnpm install' to set up the monorepo" -ForegroundColor White
Write-Host "3. Update import paths in your code" -ForegroundColor White
Write-Host "4. Run 'pnpm dev' to start development" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Your MCPVotsAGI repository is now organized for scale!" -ForegroundColor Green
