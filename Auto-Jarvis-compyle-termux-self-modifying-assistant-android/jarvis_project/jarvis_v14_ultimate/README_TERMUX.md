# JARVIS v14 Ultimate - Termux Installation Guide

## जरूरी Requirements
- **Android Device**: Android 7.0 (API 24) या higher
- **Termux App**: Latest version from F-Droid (recommended) या GitHub
- **Storage**: कम से कम 1GB free space
- **RAM**: कम से कम 2GB (4GB+ recommended)
- **Internet**: Package installation के लिए

## Quick Installation (एक Command में)

```bash
bash install_termux.sh
```

Installation complete होने के बाद:
```bash
jarvis
```

## Manual Installation (Step by Step)

### Step 1: Termux Setup

```bash
# Package lists update करें
pkg update -y && pkg upgrade -y

# Required packages install करें
pkg install -y python git wget curl termux-api nano
```

### Step 2: Storage Permission

```bash
# Storage access के लिए
termux-setup-storage
```

Permission popup में "Allow" दबाएं।

### Step 3: Project Clone/Extract

अगर आपके पास already project files हैं:
```bash
cd ~/jarvis_v14_ultimate
```

या GitHub से clone करें (if available):
```bash
git clone <repository-url>
cd jarvis_v14_ultimate
```

### Step 4: Python Dependencies

```bash
# Pip upgrade करें
python -m pip install --upgrade pip

# Dependencies install करें (5-10 minutes)
pip install -r requirements_termux.txt
```

### Step 5: Directory Structure

```bash
# Directories automatically create होंगी पहली run में
# या manually create करें:
mkdir -p ~/.jarvis/{config,data,logs,cache,backups,models,plugins}
```

### Step 6: Run JARVIS

```bash
python jarvis.py
```

या global launcher (अगर install_termux.sh use किया):
```bash
jarvis
```

## Configuration

### Memory Optimization (Termux के लिए)

JARVIS automatically Termux को detect करके memory optimize करता है:
- Maximum Memory: 150MB
- CPU Limit: 50%
- Max Threads: 2
- Cache Size: 32MB

### Manual Configuration

Config file: `~/.jarvis/config/ultimate_config.json`

```json
{
    "environment": "production",
    "optimization_profile": "termux",
    "memory_limit_mb": 150,
    "max_threads": 2,
    "enable_background_processing": false
}
```

Edit करने के लिए:
```bash
nano ~/.jarvis/config/ultimate_config.json
```

## Usage Examples

### Basic Commands

```bash
# JARVIS start करें
jarvis

# Interactive mode
jarvis --interactive

# Specific command run करें
jarvis --command "system status"

# Help देखें
jarvis --help
```

### Voice Commands (Termux-API के साथ)

```bash
# Microphone से input
jarvis --voice

# Text to speech output
jarvis --tts "Hello from JARVIS"
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'xyz'`

**Solution**:
```bash
pip install <module-name>
```

या specific package:
```bash
pip install openai anthropic requests aiohttp
```

#### 2. Memory Issues

**Problem**: "Out of memory" या app crash

**Solution**:
```bash
# Memory cleanup
python -c "import gc; gc.collect()"

# Background apps band करें
# Android settings → Apps → Force stop unused apps
```

#### 3. Permission Errors

**Problem**: "Permission denied" errors

**Solution**:
```bash
# Storage permission
termux-setup-storage

# File permissions
chmod -R u+rwx ~/.jarvis
```

#### 4. Slow Performance

**Problem**: App धीरे चल रहा है

**Solution**:
```bash
# Battery optimization disable करें
# Android settings → Apps → JARVIS → Battery → Unrestricted

# Background restrictions disable करें
# Android settings → Apps → JARVIS → Battery → Background restriction → Remove
```

### Error Logs देखें

```bash
# Latest logs
cat ~/.jarvis/logs/jarvis.log

# Live log monitoring
tail -f ~/.jarvis/logs/jarvis.log

# Error grep करें
grep -i error ~/.jarvis/logs/jarvis.log
```

## Features

### ✅ Working Features (Termux में)

- [x] AI Conversations (OpenAI, Anthropic, Groq APIs)
- [x] File Management
- [x] System Monitoring (CPU, Memory, Storage)
- [x] Task Automation
- [x] Web Requests
- [x] JSON/YAML Processing
- [x] Database Operations (SQLite)
- [x] Logging System
- [x] Configuration Management
- [x] Error Handling & Recovery
- [x] Lightweight Memory Optimization

### ⚠️ Limited Features

- [~] Heavy ML Models (Use cloud APIs instead)
- [~] Real-time Voice Recognition (Basic support via Termux-API)
- [~] Video Processing (Very slow, not recommended)
- [~] Large File Operations (Limited by mobile storage/RAM)

### ❌ Not Supported

- [ ] TensorFlow/PyTorch models (Too heavy for mobile)
- [ ] Docker containers
- [ ] GPU acceleration
- [ ] Multi-process parallelism (Memory constraints)

## Performance Optimization Tips

### 1. Reduce Memory Usage

```bash
# Config में memory limit set करें
nano ~/.jarvis/config/ultimate_config.json

# memory_limit_mb: 100-150 (Termux के लिए optimal)
```

### 2. Background Processing Disable करें

```json
{
    "enable_background_processing": false,
    "max_threads": 2
}
```

### 3. Cache Clean करें Regularly

```bash
# Cache directory clean करें
rm -rf ~/.jarvis/cache/*

# या JARVIS command से
jarvis --clean-cache
```

### 4. Old Logs Delete करें

```bash
# 7 दिन से पुराने logs delete करें
find ~/.jarvis/logs -name "*.log" -mtime +7 -delete
```

## API Keys Configuration

### OpenAI API

```bash
export OPENAI_API_KEY="your-api-key-here"
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
```

### Anthropic API

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
```

### Groq API (Free, Fast)

```bash
export GROQ_API_KEY="your-api-key-here"
echo 'export GROQ_API_KEY="your-key"' >> ~/.bashrc
```

## Uninstallation

```bash
# JARVIS files remove करें
rm -rf ~/jarvis_v14_ultimate

# Config और data remove करें
rm -rf ~/.jarvis

# Global launcher remove करें
rm -f $PREFIX/bin/jarvis
```

## Updates

```bash
# Project directory में जाएं
cd ~/jarvis_v14_ultimate

# Latest changes pull करें (if git repo)
git pull origin main

# Dependencies update करें
pip install -r requirements_termux.txt --upgrade
```

## Advanced Configuration

### Custom Paths

```python
# config/ultimate_config.py में
from utils.termux_paths import get_path_manager

pm = get_path_manager()
pm._base_paths['custom'] = Path('/custom/path')
```

### Custom Optimization Profile

```python
# utils/mobile_optimizer.py में
PROFILES['custom'] = MobileOptimizationProfile(
    max_memory_mb=200,
    max_cpu_percent=60.0,
    max_threads=3,
    # ... other settings
)
```

## Development

### Running Tests

```bash
# Compatibility test
python test_termux_compatibility.py

# Full test suite
python run_comprehensive_tests.py
```

### Debug Mode

```bash
# Debug logs enable करें
jarvis --debug

# या config में
{
    "logging": {
        "level": "DEBUG"
    }
}
```

## Support & Community

### Getting Help

1. **Error Logs**: सबसे पहले logs check करें
   ```bash
   cat ~/.jarvis/logs/jarvis.log | tail -50
   ```

2. **Test Suite**: Compatibility check करें
   ```bash
   python test_termux_compatibility.py
   ```

3. **Documentation**: यह file और code comments पढ़ें

### Contributing

अगर आप improve करना चाहते हैं:
1. Issues report करें
2. Pull requests submit करें
3. Documentation improve करें

## Credits

- **Development Team**: JARVIS Development Team
- **Version**: 14.0.0 Ultimate
- **Platform**: Termux (Android)
- **License**: [Your License]

## Changelog

### v14.0.0 Ultimate
- ✅ Full Termux compatibility
- ✅ Mobile optimization (150MB memory)
- ✅ Automatic platform detection
- ✅ One-command installation
- ✅ Lightweight dependencies (500MB vs 3.5GB)
- ✅ 94%+ test coverage
- ✅ Comprehensive error handling
- ✅ Path management for all platforms

---

## Quick Reference

```bash
# Installation
bash install_termux.sh

# Start JARVIS
jarvis

# Help
jarvis --help

# Update
cd ~/jarvis_v14_ultimate && git pull && pip install -r requirements_termux.txt --upgrade

# Logs
tail -f ~/.jarvis/logs/jarvis.log

# Clean cache
rm -rf ~/.jarvis/cache/*

# Uninstall
rm -rf ~/jarvis_v14_ultimate ~/.jarvis $PREFIX/bin/jarvis
```

---

**Happy coding with JARVIS on Termux! 🚀📱**
