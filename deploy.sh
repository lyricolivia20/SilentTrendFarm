#!/bin/bash

# SilentTrendFarm Deployment Script
echo "🚀 Deploying SilentTrendFarm to Netlify"
echo "========================================"

# Check if netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo "❌ Netlify CLI not found. Installing..."
    npm install -g netlify-cli
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and add your API keys"
fi

# Build the project
echo "🔨 Building project..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please fix errors and try again."
    exit 1
fi

echo "✅ Build successful!"

# Check if site is linked
if [ ! -f .netlify/state.json ]; then
    echo "🔗 Linking to Netlify site..."
    netlify link
fi

# Deploy
echo "📤 Deploying to Netlify..."
netlify deploy --prod

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "📊 View your site:"
    netlify open:site
    echo ""
    echo "📝 View function logs:"
    netlify functions:list
else
    echo "❌ Deployment failed. Check the errors above."
    exit 1
fi
