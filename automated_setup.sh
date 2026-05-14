#!/bin/bash

# =============================================================================
# Finance Dashboard - Automated Setup Script
# =============================================================================
# This script automates the entire deployment process
# Usage: ./automated_setup.sh
# =============================================================================

set -e  # Exit on any error

echo "🚀 Finance Dashboard - Automated Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="finance-dashboard"
GITHUB_USER="prashant1gaurav-ppsl"
GITHUB_REPO="https://github.com/$GITHUB_USER/$REPO_NAME.git"

# =============================================================================
# Step 1: Check Prerequisites
# =============================================================================
echo "📋 Step 1: Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git found${NC}"

# =============================================================================
# Step 2: Setup Local Repository
# =============================================================================
echo ""
echo "📁 Step 2: Setting up local repository..."

# Check if we're already in the finance_dashboard directory
if [ "$(basename "$PWD")" = "finance_dashboard" ]; then
    echo -e "${YELLOW}Already in finance_dashboard directory${NC}"
else
    if [ -d "finance_dashboard" ]; then
        echo -e "${YELLOW}finance_dashboard directory exists${NC}"
        read -p "Delete and recreate? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            rm -rf finance_dashboard
            echo "Deleted old directory"
        else
            echo "Using existing directory"
        fi
    fi
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git config user.email "prashanrav@paytments.com"
    git config user.name "Prashant Gaurav"
    echo -e "${GREEN}✅ Git initialized${NC}"
else
    echo -e "${GREEN}✅ Git already initialized${NC}"
fi

# =============================================================================
# Step 3: Check for Sensitive Data
# =============================================================================
echo ""
echo "🔒 Step 3: Security check..."

# Check for hardcoded credentials
if grep -r "prrav01\|prashanrav@paytments.com" . --exclude-dir=.git --exclude="*.sh" 2>/dev/null; then
    echo -e "${RED}⚠️  WARNING: Found potential credentials in files!${NC}"
    echo "Please review and remove before pushing to public repository"
    read -p "Continue anyway? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ No hardcoded credentials found${NC}"
fi

# =============================================================================
# Step 4: Commit Changes
# =============================================================================
echo ""
echo "💾 Step 4: Committing changes..."

git add .

if git diff --cached --quiet; then
    echo -e "${YELLOW}No changes to commit${NC}"
else
    git commit -m "Secure finance dashboard setup"
    echo -e "${GREEN}✅ Changes committed${NC}"
fi

# Ensure we're on main branch
if [ "$(git branch --show-current)" != "main" ]; then
    git branch -M main
    echo "Renamed branch to main"
fi

# =============================================================================
# Step 5: GitHub Setup
# =============================================================================
echo ""
echo "🌐 Step 5: GitHub repository setup..."

# Check if remote exists
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Remote 'origin' already exists${NC}"
    CURRENT_REMOTE=$(git remote get-url origin)
    if [ "$CURRENT_REMOTE" != "$GITHUB_REPO" ]; then
        echo "Current remote: $CURRENT_REMOTE"
        echo "Expected remote: $GITHUB_REPO"
        read -p "Update remote? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            git remote set-url origin "$GITHUB_REPO"
            echo -e "${GREEN}✅ Remote updated${NC}"
        fi
    else
        echo -e "${GREEN}✅ Remote already configured correctly${NC}"
    fi
else
    git remote add origin "$GITHUB_REPO"
    echo -e "${GREEN}✅ Remote added${NC}"
fi

# =============================================================================
# Step 6: Push to GitHub
# =============================================================================
echo ""
echo "📤 Step 6: Pushing to GitHub..."
echo ""
echo -e "${YELLOW}⚠️  You will be asked for GitHub credentials:${NC}"
echo "   Username: $GITHUB_USER"
echo "   Password: Use Personal Access Token (not GitHub password)"
echo ""
echo "To create token: https://github.com/settings/tokens"
echo "   1. Click 'Generate new token (classic)'"
echo "   2. Select 'repo' scope"
echo "   3. Copy the token and use as password"
echo ""
read -p "Press Enter when ready to push..."

if git push -u origin main --force; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
else
    echo -e "${RED}❌ Push failed. Check your credentials and try again${NC}"
    exit 1
fi

# =============================================================================
# Step 7: Next Steps
# =============================================================================
echo ""
echo "🎉 Local setup complete!"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📋 NEXT STEPS - Manual (Browser):"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  Make Repository Public:"
echo "    → https://github.com/$GITHUB_USER/$REPO_NAME/settings"
echo "    → Scroll to 'Danger Zone'"
echo "    → Click 'Change visibility' → 'Make public'"
echo ""
echo "2️⃣  Deploy on Streamlit Cloud:"
echo "    → Go to: https://share.streamlit.io/"
echo "    → Click 'New app'"
echo "    → Repository: $GITHUB_USER/$REPO_NAME"
echo "    → Branch: main"
echo "    → Main file: app.py"
echo "    → Click 'Deploy'"
echo ""
echo "3️⃣  Add Secrets (IMPORTANT!):"
echo "    → In Streamlit app dashboard"
echo "    → Settings → Secrets"
echo "    → Copy from secrets.example.toml"
echo "    → Add your actual Trino credentials"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📄 Your repository: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo -e "${GREEN}🎊 All automated steps completed successfully!${NC}"
