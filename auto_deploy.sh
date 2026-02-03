#!/bin/bash

echo "╔═══════════════════════════════════════╗"
echo "║  💀 AUTO DEPLOY - OSINT Bot 💀        ║"
echo "║     by P1yu5h69                       ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not installed. Install it first!"
    exit 1
fi

echo "🔧 Step 1: Git Setup..."
git init
git add .
git commit -m "OSINT Bot by P1yu5h69"
git branch -M main
echo "✅ Git initialized!"
echo ""

# Get GitHub username
echo "📝 Enter your GitHub username:"
read github_username

if [ -z "$github_username" ]; then
    echo "❌ Username cannot be empty!"
    exit 1
fi

# Set remote
repo_url="https://github.com/$github_username/osint-bot.git"
echo ""
echo "🔗 Setting remote: $repo_url"
git remote add origin $repo_url 2>/dev/null || git remote set-url origin $repo_url

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║         IMPORTANT STEPS               ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "1️⃣  Create PRIVATE repo on GitHub:"
echo "    👉 https://github.com/new"
echo "    - Repository name: osint-bot"
echo "    - ✅ Select 'Private'"
echo "    - Click 'Create repository'"
echo ""
echo "2️⃣  Press ENTER after creating repo..."
read -p ""

echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║    FINAL STEP: Deploy on Render      ║"
    echo "╚═══════════════════════════════════════╝"
    echo ""
    echo "🌐 Opening Render.com..."
    
    # Open Render.com
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "https://render.com/select-repo?type=web"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "https://render.com/select-repo?type=web"
    fi
    
    echo ""
    echo "📋 Follow these steps on Render:"
    echo ""
    echo "1. Sign in with GitHub"
    echo "2. Select 'osint-bot' repository"
    echo "3. Settings will auto-fill"
    echo "4. Add Environment Variable:"
    echo "   Key: BOT_TOKEN"
    echo "   Value: 8367270183:AAE1AlWPm1A3ILFulA-OnEFpVP_LkjDomp0"
    echo "5. Click 'Create Web Service'"
    echo ""
    echo "✅ Bot will be online 24/7 in 5-10 minutes!"
    echo ""
    echo "💀 BLACKHAT COMRADE - by P1yu5h69 🔥"
else
    echo ""
    echo "❌ Push failed! Make sure:"
    echo "   1. You created the repo on GitHub"
    echo "   2. Repo name is 'osint-bot'"
    echo "   3. You have internet connection"
    echo ""
    echo "Try again: ./auto_deploy.sh"
fi
