#!/bin/bash

# GPU Instance Quick Setup Script
# Run this on your GPU instance after connecting

set -e  # Exit on error

echo "=================================================="
echo "GPU Instance Setup for IDE Index Project"
echo "=================================================="
echo ""

# Check if we're on GPU instance
if [ "$USER" != "haitham" ]; then
    echo "⚠️  Warning: Expected user 'haitham', got '$USER'"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✓ Connected as user: $USER"
echo ""

# Detect package manager
if command -v yum &> /dev/null; then
    PACKAGE_MANAGER="yum"
    UPDATE_CMD="sudo yum update -y"
    INSTALL_CMD="sudo yum install -y"
    # Install EPEL for RHEL/CentOS
    echo "📦 Installing EPEL repository..."
    sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
elif command -v apt &> /dev/null; then
    PACKAGE_MANAGER="apt"
    UPDATE_CMD="sudo apt update && sudo apt upgrade -y"
    INSTALL_CMD="sudo apt install -y"
elif command -v dnf &> /dev/null; then
    PACKAGE_MANAGER="dnf"
    UPDATE_CMD="sudo dnf update -y"
    INSTALL_CMD="sudo dnf install -y"
else
    echo "❌ No supported package manager found (yum, apt, dnf)"
    exit 1
fi

echo "✓ Detected package manager: $PACKAGE_MANAGER"
echo ""

# Update system
echo "📦 Updating system packages..."
$UPDATE_CMD
echo "✓ System updated"
echo ""

# Install required packages
echo "🔧 Installing required packages..."
if [ "$PACKAGE_MANAGER" = "yum" ]; then
    $INSTALL_CMD git python3 python3-pip python3-virtualenv htop tmux curl unzip
else
    $INSTALL_CMD git python3 python3-pip python3-venv htop tmux curl unzip
fi
echo "✓ Packages installed"
echo ""

# Verify GPU
echo "🎮 Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits
    echo "✓ GPU detected"
else
    echo "⚠️  No NVIDIA GPU detected"
fi
echo ""

# Check CUDA
echo "🔥 Checking CUDA..."
if command -v nvcc &> /dev/null; then
    nvcc --version | grep "release"
    echo "✓ CUDA available"
else
    echo "⚠️  CUDA not found - will use CPU mode"
fi
echo ""

# Clone or setup project
if [ -d "ide-index-extraction" ]; then
    echo "📁 Project directory exists"
    cd ide-index-extraction
    echo "Updating repository..."
    git pull origin main 2>/dev/null || echo "Could not update - continuing"
else
    echo "📥 Cloning repository..."
    # You'll need to replace with your actual repo URL
    echo "⚠️  Please provide your GitHub repository URL:"
    echo "Example: https://github.com/YOUR_USERNAME/ide-index-extraction.git"
    read -p "Repository URL: " repo_url
    git clone "$repo_url" ide-index-extraction
    cd ide-index-extraction
fi
echo "✓ Project ready"
echo ""

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
echo "✓ Virtual environment created"
echo ""

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Setup configuration
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
else
    echo "✓ .env file exists"
fi

echo ""
echo "🔑 IMPORTANT: Configure your OpenAI API key"
echo "Edit .env file: nano .env"
echo "Add: OPENAI_API_KEY=sk-your-api-key-here"
echo ""

# Create directories
mkdir -p data outputs database
echo "✓ Directories created"
echo ""

# Run pre-flight check
echo "🧪 Running pre-flight check..."
python preflight_check.py
echo ""

# Final instructions
echo "=================================================="
echo "SETUP COMPLETE! 🎉"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add your OpenAI API key:"
echo "   nano .env"
echo ""
echo "2. Upload PDF files to data/ folder:"
echo "   # From your local machine:"
echo "   scp *.pdf haitham@136.112.60.210:~/ide-index-extraction/data/"
echo ""
echo "3. Run the extraction:"
echo "   source venv/bin/activate"
echo "   python src/main.py --max-chunks 5"
echo ""
echo "4. Monitor progress:"
echo "   nvidia-smi    # GPU usage"
echo "   htop         # System resources"
echo ""
echo "=================================================="
echo "GPU Instance: $(hostname -I | awk '{print $1}')"
echo "Project Path: $(pwd)"
echo "=================================================="
