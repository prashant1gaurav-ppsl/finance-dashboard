#!/bin/bash

# Quick Deployment Script for Finance Dashboard
# Run this script to set everything up automatically

echo "🚀 Finance Dashboard - Quick Setup"
echo "=================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

echo "📝 Step 1: Git Repository Setup"
echo "-------------------------------"

# Initialize git if not already initialized
if [ ! -d .git ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "ℹ️  Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
.streamlit/secrets.toml
.env
*.log
.DS_Store
EOF
    echo "✅ .gitignore created"
fi

# Add all files
git add .
git status

echo ""
echo "📋 Step 2: Ready to Commit"
echo "-------------------------"
read -p "Enter commit message (default: 'Initial commit'): " commit_msg
commit_msg=${commit_msg:-"Initial commit"}

git commit -m "$commit_msg"
echo "✅ Files committed"

echo ""
echo "🌐 Step 3: GitHub Setup"
echo "----------------------"
echo "Next steps:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   → Go to: https://github.com/new"
echo "   → Name: finance-dashboard"
echo "   → Make it PRIVATE for security"
echo ""
echo "2. Connect and push:"
read -p "Enter your GitHub username: " github_user
read -p "Enter repository name (default: finance-dashboard): " repo_name
repo_name=${repo_name:-"finance-dashboard"}

echo ""
echo "Run these commands:"
echo ""
echo "git branch -M main"
echo "git remote add origin https://github.com/$github_user/$repo_name.git"
echo "git push -u origin main"
echo ""

read -p "Do you want to run these commands now? (y/n): " run_now

if [ "$run_now" = "y" ] || [ "$run_now" = "Y" ]; then
    git branch -M main
    git remote add origin https://github.com/$github_user/$repo_name.git
    git push -u origin main
    echo "✅ Pushed to GitHub!"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next Steps:"
echo "1. Go to: https://share.streamlit.io/"
echo "2. Click 'New app'"
echo "3. Select your GitHub repository: $github_user/$repo_name"
echo "4. Main file: app.py"
echo "5. Click Deploy!"
echo ""
echo "🔐 Add Secrets in Streamlit Cloud:"
echo "   Settings → Secrets → Add your Trino credentials"
echo ""
echo "Your dashboard will be live at:"
echo "https://YOUR_APP_NAME.streamlit.app"
echo ""
