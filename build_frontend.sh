#!/bin/bash
cd /mnt/c/Workspace/MCPVotsAGI/frontend

echo "🚀 Building Ultimate AGI Frontend..."
echo "=================================="

# Set environment variables
export NEXT_PUBLIC_SENTRY_DISABLED=true
export NODE_ENV=production

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf .next
rm -rf out

# Run the build
echo "🏗️ Starting build process..."
npm run build

echo "✅ Build complete!"