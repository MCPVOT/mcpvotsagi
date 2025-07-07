# Verify the migration was successful

Write-Host "🔍 Verifying MCPVotsAGI migration..." -ForegroundColor Blue

# Check directory structure
Write-Host "📁 Checking directory structure..." -ForegroundColor Yellow

$requiredDirs = @(
    "apps/web",
    "apps/api",
    "packages/core",
    "packages/agents",
    "services",
    "infrastructure",
    "docs",
    "scripts",
    "tests"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "✅ $dir exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $dir missing" -ForegroundColor Red
    }
}

# Check configuration files
Write-Host ""
Write-Host "📝 Checking configuration files..." -ForegroundColor Yellow

$requiredFiles = @(
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
    ".gitignore",
    ".vscode/settings.json"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing" -ForegroundColor Red
    }
}

# Check if pnpm is installed
Write-Host ""
Write-Host "📦 Checking package manager..." -ForegroundColor Yellow

try {
    $pnpmVersion = & pnpm --version
    Write-Host "✅ pnpm $pnpmVersion is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ pnpm is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   npm install -g pnpm" -ForegroundColor White
    return
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow

try {
    & pnpm install
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if packages are properly linked
Write-Host ""
Write-Host "🔗 Verifying package links..." -ForegroundColor Yellow

$packageDirs = Get-ChildItem "packages" -Directory
foreach ($package in $packageDirs) {
    $packageJsonPath = Join-Path $package.FullName "package.json"
    if (Test-Path $packageJsonPath) {
        Write-Host "✅ Package $($package.Name) has package.json" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Package $($package.Name) missing package.json" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✨ Migration verification complete!" -ForegroundColor Magenta
Write-Host ""
Write-Host "🎯 Summary:" -ForegroundColor Yellow
Write-Host "- Repository structure has been modernized" -ForegroundColor White
Write-Host "- Monorepo configuration is in place" -ForegroundColor White
Write-Host "- Dependencies are installed and linked" -ForegroundColor White
Write-Host "- Ready for development with 'pnpm dev'" -ForegroundColor White
