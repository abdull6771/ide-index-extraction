# 🚀 GPU Instance Setup Guide

## Connect to Your GPU Instance

### Step 1: SSH Connection

```bash
# Connect to your GPU instance
ssh haitham@136.112.60.210

# Enter password when prompted: w3eb6Ews3hGH5e8
```

### Step 2: Verify GPU Access

```bash
# Check if GPU is available
nvidia-smi

# Check CUDA version
nvcc --version

# Check available memory
free -h
df -h
```

### Step 3: Update System

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git python3 python3-pip python3-venv htop tmux
```

---

## 📦 Clone and Setup Project

### Step 1: Clone Repository

```bash
# Clone your repository (replace with your GitHub username)
git clone https://github.com/YOUR_USERNAME/ide-index-extraction.git
cd ide-index-extraction

# Or if you have the files locally, upload them:
# scp -r /path/to/local/project haitham@136.112.60.210:~/
```

### Step 1.5: Quick Setup (Recommended)

```bash
# Run the automated setup script (if available)
./gpu_setup.sh

# This will handle:
# - System updates
# - Package installation
# - Virtual environment setup
# - Dependency installation
# - Directory creation
# - Pre-flight checks
```

### Step 2: Create Virtual Environment

```bash
# Create Python virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installations
python -c "import langchain, openai, pydantic; print('✓ All imports working')"
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your OpenAI API key
nano .env

# Add your API key:
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Step 5: Add PDF Files

```bash
# Create data directory if needed
mkdir -p data

# Upload your PDF files (from your local machine)
# On your local machine, run:
# scp /path/to/your/reports/*.pdf haitham@136.112.60.210:~/ide-index-extraction/data/

# Or if you have them in a zip file:
# scp reports.zip haitham@136.112.60.210:~/
# Then on GPU instance: unzip reports.zip -d data/
```

---

## 🏃‍♂️ Run the Project

### Option 1: Full Pipeline (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Run pre-flight check
python preflight_check.py

# Run full extraction
python src/main.py
```

### Option 2: Memory-Efficient Mode (For Large PDFs)

```bash
# Process with limited chunks to save memory
python src/main.py --max-chunks 10

# Or process one PDF at a time
python examples/process_single_pdf.py data/your-file.pdf --max-chunks 5
```

### Option 3: Use TMUX for Background Processing

```bash
# Start tmux session
tmux new -s extraction

# Run the pipeline
source venv/bin/activate
python src/main.py --max-chunks 5

# Detach from tmux (Ctrl+B, then D)
# Reattach later: tmux attach -t extraction
```

---

## 📊 Monitor Progress

### Check GPU Usage

```bash
# Monitor GPU usage
watch -n 5 nvidia-smi

# Monitor system resources
htop

# Check disk space
df -h
```

### Check Pipeline Progress

```bash
# Use the monitoring script (recommended)
./gpu_monitor.sh

# Or check manually:
# View current status
tail -f nohup.out  # If running in background

# Check database growth
ls -lh database/
sqlite3 database/ide_index.db "SELECT COUNT(*) FROM digital_initiatives;"

# Check output files
ls -lh outputs/
```

---

## 📁 Transfer Results Back

### Download Results to Local Machine

```bash
# On your local machine, download results:
scp haitham@136.112.60.210:~/ide-index-extraction/database/ide_index.db ./
scp haitham@136.112.60.210:~/ide-index-extraction/outputs/*.json ./

# Or download everything:
scp -r haitham@136.112.60.210:~/ide-index-extraction/results/ ./
```

---

## 🔧 Troubleshooting GPU Issues

### Memory Issues

```bash
# If getting killed due to memory:
python src/main.py --max-chunks 5

# Check memory usage
free -h
nvidia-smi
```

### CUDA Issues

```bash
# Check CUDA installation
nvcc --version
python -c "import torch; print(torch.cuda.is_available())"

# If CUDA not working, use CPU mode
# Edit .env: OPENAI_MODEL=gpt-3.5-turbo
```

### Network Issues

```bash
# Test internet connection
ping -c 3 google.com

# Test OpenAI API access
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
```

---

## 💰 Cost Monitoring

### Check API Usage

```bash
# Monitor your OpenAI usage
# Visit: https://platform.openai.com/usage

# Estimate costs:
# GPT-4o-mini: ~$0.01-0.02 per document
# GPT-4o: ~$0.10-0.20 per document
```

---

## 🛡️ Security Best Practices

### On GPU Instance

```bash
# Change default password immediately
passwd

# Update SSH config for better security
sudo nano /etc/ssh/sshd_config
# Add: PasswordAuthentication no
# Add: PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

### API Key Security

```bash
# Never expose API key in logs
# Use environment variables only
# Rotate keys regularly
```

---

## 📋 Complete Workflow

### 1. Initial Setup

```bash
ssh haitham@136.112.60.210
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-venv htop tmux
```

### 2. Project Setup

```bash
git clone https://github.com/YOUR_USERNAME/ide-index-extraction.git
cd ide-index-extraction
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add your API key
```

### 3. Upload Data

```bash
# From local machine:
scp *.pdf haitham@136.112.60.210:~/ide-index-extraction/data/
```

### 4. Run Extraction

```bash
source venv/bin/activate
python preflight_check.py
python src/main.py --max-chunks 10
```

### 5. Monitor & Download

```bash
# Monitor: htop, nvidia-smi
# Download results when done
```

---

## 🎯 Quick Commands Reference

```bash
# Connect
ssh haitham@136.112.60.210

# Setup
cd ide-index-extraction
source venv/bin/activate

# Run
python src/main.py --max-chunks 5

# Monitor
nvidia-smi
htop

# Download results
# (from local machine)
scp haitham@136.112.60.210:~/ide-index-extraction/outputs/*.json ./
```

---

## 🚨 Emergency Commands

### If Process Gets Killed

```bash
# Restart with smaller chunks
python src/main.py --max-chunks 3

# Check system resources
free -h
nvidia-smi
```

### If SSH Disconnects

```bash
# Use tmux to keep processes running
tmux new -s extraction
python src/main.py --max-chunks 5
# Ctrl+B, D to detach
# tmux attach -t extraction  # to reattach
```

### If Out of Disk Space

```bash
# Clean up
rm -rf venv/
du -h --max-depth=1
df -h
```

---

## 📞 Support

If you encounter issues:

1. **Check logs**: Look for error messages in terminal output
2. **Verify setup**: Run `python preflight_check.py`
3. **Check resources**: Use `nvidia-smi` and `htop`
4. **Test small**: Start with `--max-chunks 3`

---

**Ready to start?** Connect to your GPU instance and follow the steps above! 🚀

**GPU Instance:** `ssh haitham@136.112.60.210`  
**Password:** `w3eb6Ews3hGH5e8`
