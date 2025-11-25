#!/bin/bash
# Helper script to set up GitHub repository for Netlify deployment

echo "🚀 Setting up GitHub repository for Netlify deployment..."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) not found."
    echo "   Install it: brew install gh"
    echo "   Or create repo manually at: https://github.com/new"
    exit 1
fi

# Check if already has remote
if git remote -v | grep -q origin; then
    echo "✅ Git remote already configured"
    git remote -v
else
    read -p "Enter your GitHub username: " GITHUB_USER
    read -p "Enter repository name (default: wheat-bot-dashboard): " REPO_NAME
    REPO_NAME=${REPO_NAME:-wheat-bot-dashboard}
    
    echo ""
    echo "Creating repository: $GITHUB_USER/$REPO_NAME"
    
    # Create repo and push
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
    
    echo ""
    echo "✅ Repository created and pushed!"
    echo "   URL: https://github.com/$GITHUB_USER/$REPO_NAME"
fi

echo ""
echo "📋 Next steps:"
echo "1. Go to https://app.netlify.com"
echo "2. Click 'Add new site' → 'Import an existing project'"
echo "3. Choose GitHub and select your repository"
echo "4. Set environment variable: NETLIFY_DATABASE_URL"
echo "5. Deploy!"
echo ""
echo "See DEPLOY_VIA_GIT.md for detailed instructions"

