# ThreatFusion Troubleshooting Guide

This guide covers common issues you might encounter when installing and using ThreatFusion.

---

## Installation Issues

### ❌ Error: `externally-managed-environment`

**Full error message:**
```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install...
```

**Cause:** Modern Linux/WSL distributions prevent direct `pip install` to protect system Python.

**Solution:** Use Poetry instead of pip:
```bash
# DON'T do this:
pip install -r requirements.txt

# DO this instead:
poetry install
```

---

### ⚠️ Warning: `The current project could not be installed`

**Full warning:**
```
Warning: The current project could not be installed: No file/folder found for package threatfusion
```

**Cause:** Poetry couldn't find the package configuration.

**Solution:** This has been fixed in the latest version. If you still see this, run:
```bash
poetry install --no-root
```

---

### ❌ Error: `ModuleNotFoundError: No module named 'click'`

**Cause:** Dependencies weren't installed, or you're not running inside the Poetry environment.

**Solution:**
```bash
# First, make sure dependencies are installed
poetry install

# Then use 'poetry run' to execute commands
poetry run python -m src.main enrich 8.8.8.8
```

---

### ❌ Error: `ModuleNotFoundError: No module named 'src'`

**Cause:** Running the script incorrectly without Poetry or from wrong directory.

**Solution:** Always use one of these methods:
```bash
# Method 1: Use the shortcut command (recommended)
poetry run threatfusion enrich 8.8.8.8

# Method 2: Run as a module
poetry run python -m src.main enrich 8.8.8.8

# DON'T do this - it won't work:
python src/main.py enrich 8.8.8.8
```

---

## Configuration Issues

### ❌ Error: `No API keys configured`

**Cause:** The `.env` file doesn't exist or has placeholder values.

**Solution:**
```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit it with your API keys
nano .env  # or use any text editor

# 3. Verify configuration
poetry run threatfusion config-check
```

---

### ⚠️ Can't see `.env` file

**Cause:** Files starting with `.` are hidden in Linux/WSL.

**Solution:**
```bash
# View hidden files
ls -a

# Edit .env directly
nano .env
```

---

## Runtime Issues

### ❌ Error: `Rate limit exceeded`

**Cause:** You've hit the API rate limit for a service (common with free tiers).

**Solution:**
- Wait 24 hours for free tier limits to reset
- Upgrade to a paid API plan
- Use different API keys

---

### ⚠️ Warning: Private IP address

**Message:**
```
⚠️  Warning: 192.168.1.1 is a private/non-routable IP address
   External threat intelligence sources may not have data
```

**Cause:** You're querying a private IP (192.168.x.x, 10.x.x.x, etc.)

**Solution:** This is just a warning. External threat intel sources won't have data about private IPs, which is expected.

---

### ❌ Timeout errors

**Cause:** API services are slow or unreachable.

**Solution:**
```bash
# Increase timeout (default is 30 seconds)
poetry run threatfusion enrich 8.8.8.8 --timeout 60
```

---

## Performance Issues

### Slow query execution

**Causes:**
- Network latency
- API rate limiting
- Too many workers

**Solutions:**
```bash
# Reduce concurrent workers in .env
MAX_WORKERS=4  # Default is 8

# Or use a longer timeout
poetry run threatfusion enrich <indicator> --timeout 60
```

---

## Environment Issues

### Python version mismatch

**Error:** `Python version not compatible`

**Solution:** ThreatFusion requires Python 3.11+
```bash
# Check your version
python3 --version

# If < 3.11, install newer Python
sudo apt update
sudo apt install python3.11
```

---

## Getting Help

If none of these solutions work:

1. **Check the logs** in the console output
2. **Verify API keys** are correct at the provider websites
3. **Test individual APIs** using their documentation
4. **File an issue** on GitHub with:
   - Full error message
   - Python version (`python3 --version`)
   - Poetry version (`poetry --version`)
   - Operating system
