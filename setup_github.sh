#!/bin/bash

# Exercise Monitoring Vest - GitHub Setup Script
# This script automates the process of organizing and pushing to GitHub

set -e  # Exit on error

echo "=========================================="
echo "Exercise Monitoring Vest - GitHub Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed!"
    echo "Install git first:"
    echo "  Mac: brew install git"
    echo "  Linux: sudo apt-get install git"
    exit 1
fi

print_success "Git is installed: $(git --version)"
echo ""

# Check if git is configured
if [ -z "$(git config --global user.name)" ]; then
    print_warning "Git user.name not configured"
    read -p "Enter your name: " git_name
    git config --global user.name "$git_name"
fi

if [ -z "$(git config --global user.email)" ]; then
    print_warning "Git user.email not configured"
    read -p "Enter your email: " git_email
    git config --global user.email "$git_email"
fi

print_success "Git configured as: $(git config --global user.name) <$(git config --global user.email)>"
echo ""

# Ask for GitHub repository details
echo "=========================================="
echo "Repository Information"
echo "=========================================="
echo ""

read -p "Enter your GitHub username: " github_username
read -p "Enter repository name (default: exercise-monitoring-vest): " repo_name
repo_name=${repo_name:-exercise-monitoring-vest}

github_url="https://github.com/$github_username/$repo_name.git"

echo ""
print_info "Repository URL will be: $github_url"
echo ""

# Ask if repository exists
read -p "Does the repository already exist on GitHub? (y/n): " repo_exists

echo ""
echo "=========================================="
echo "Setting Up Repository Structure"
echo "=========================================="
echo ""

# Create directory structure
print_info "Creating directory structure..."

mkdir -p arduino/main
mkdir -p arduino/libraries/{ECGProcessor,RespiratoryProcessor,GSRProcessor,DataLogger}
mkdir -p arduino/examples/{ecg_test,respiratory_test,gsr_test}
mkdir -p web-dashboard
mkdir -p docs/{circuit-diagrams,datasheets}
mkdir -p hardware/wiring-diagrams
mkdir -p data

print_success "Directory structure created"
echo ""

# Move web dashboard files
print_info "Moving web dashboard files..."

if [ -f "exercise_vest_dashboard.html" ]; then
    mv exercise_vest_dashboard.html web-dashboard/dashboard.html
    print_success "Moved dashboard.html"
fi

if [ -f "serial_bridge.py" ]; then
    mv serial_bridge.py web-dashboard/
    print_success "Moved serial_bridge.py"
fi

if [ -f "test_data_generator.py" ]; then
    mv test_data_generator.py web-dashboard/
    print_success "Moved test_data_generator.py"
fi

if [ -f "requirements.txt" ]; then
    mv requirements.txt web-dashboard/
    print_success "Moved requirements.txt"
fi

if [ -f "README_DASHBOARD.md" ]; then
    mv README_DASHBOARD.md web-dashboard/README.md
    print_success "Moved web dashboard README"
fi

echo ""

# Initialize git if needed
if [ ! -d ".git" ]; then
    print_info "Initializing git repository..."
    git init
    print_success "Git repository initialized"
else
    print_info "Git repository already initialized"
fi

echo ""

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    print_info "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Arduino
*.hex
*.eep
*.elf
*.o
*.su
.DS_Store

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# IDEs
.vscode/
.idea/

# Test Data
data/test_*
data/SESSION_*/

# Logs
*.log
logs/
EOF
    print_success ".gitignore created"
else
    print_info ".gitignore already exists"
fi

echo ""

# Stage all files
print_info "Staging all files..."
git add .

echo ""

# Show what will be committed
print_info "Files to be committed:"
git status --short

echo ""
read -p "Proceed with commit? (y/n): " proceed_commit

if [ "$proceed_commit" != "y" ]; then
    print_warning "Commit cancelled"
    exit 0
fi

# Commit
print_info "Creating commit..."
git commit -m "Initial commit: Exercise Monitoring Vest project

- Complete Arduino firmware with multi-sensor integration
- Real-time web dashboard with live visualization
- Comprehensive documentation
- Example data and test utilities" || print_warning "No changes to commit"

print_success "Commit created"
echo ""

# Set up remote
if git remote | grep -q "origin"; then
    print_info "Remote 'origin' already exists"
    current_url=$(git remote get-url origin)
    print_info "Current URL: $current_url"
    
    read -p "Update remote URL? (y/n): " update_remote
    if [ "$update_remote" = "y" ]; then
        git remote set-url origin "$github_url"
        print_success "Remote URL updated"
    fi
else
    print_info "Adding remote 'origin'..."
    git remote add origin "$github_url"
    print_success "Remote added: $github_url"
fi

echo ""

# Push to GitHub
if [ "$repo_exists" = "y" ]; then
    print_info "Pushing to existing repository..."
    echo ""
    print_warning "If you get a permission error, make sure you have:"
    print_warning "1. Created the repository on GitHub"
    print_warning "2. Have access rights to push"
    echo ""
    
    # Ensure we're on main branch
    git branch -M main
    
    # Push
    if git push -u origin main; then
        print_success "Successfully pushed to GitHub!"
    else
        print_error "Push failed. Common solutions:"
        echo "  1. Make sure the repository exists on GitHub"
        echo "  2. Check your GitHub credentials"
        echo "  3. Try: git pull origin main --rebase"
        echo "     Then: git push origin main"
        exit 1
    fi
else
    print_warning "Repository doesn't exist on GitHub yet"
    echo ""
    echo "Please:"
    echo "  1. Go to https://github.com/new"
    echo "  2. Create a repository named: $repo_name"
    echo "  3. Don't initialize with README, .gitignore, or license"
    echo "  4. Run this command after creating:"
    echo ""
    echo "     git push -u origin main"
    echo ""
fi

echo ""
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
print_success "Your repository is ready!"
echo ""
echo "Repository URL: https://github.com/$github_username/$repo_name"
echo ""
echo "Next steps:"
echo "  1. View your repository on GitHub"
echo "  2. Add description and topics"
echo "  3. Share with team members"
echo ""
echo "To push future changes:"
echo "  git add ."
echo "  git commit -m \"Your commit message\""
echo "  git push origin main"
echo ""
