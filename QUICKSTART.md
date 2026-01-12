# 🚀 ThreatFusion Quick Start Guide

Get up and running with ThreatFusion in **5 minutes**.

---

## Step 1: Install Poetry

Poetry is required to manage dependencies. If you don't have it:

```bash
# Linux/WSL/macOS
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Verify:
```bash
poetry --version
```

---

## Step 2: Install ThreatFusion

```bash
# Clone the repository
git clone https://github.com/yourusername/threatfusion.git
cd threatfusion

# Install all dependencies
poetry install
```

> **Why Poetry?** Modern Linux/WSL systems block `pip install` globally. Poetry creates an isolated environment automatically.

---

## Step 3: Configure API Keys

```bash
# Copy example config
cp .env.example .env

# Edit with your API keys
nano .env
```

Add at least **one** API key:
```ini
VT_API_KEY=your_key_here
SHODAN_API_KEY=your_key_here
# ... add more as needed
```

> **Note:** Files starting with `.` are hidden. Use `ls -a` to see them.

### Where to get API keys?

| Service | Link |
|---------|------|
| VirusTotal | [virustotal.com/gui/join-us](https://www.virustotal.com/gui/join-us) |
| Shodan | [account.shodan.io/register](https://account.shodan.io/register) |
| Censys | [censys.io/register](https://censys.io/register) |
| OTX | [otx.alienvault.com/api](https://otx.alienvault.com/api) |
| AbuseIPDB | [abuseipdb.com/register](https://www.abuseipdb.com/register) |

---

## Step 4: Verify Setup

```bash
poetry run threatfusion config-check
```

**Expected output:**
```
┌─────────────────────────────────────┐
│  API Services Status                │
├─────────────────────────────────────┤
│ VIRUSTOTAL    ✓ Configured  Ready   │
│ SHODAN        ✓ Configured  Ready   │
└─────────────────────────────────────┘

Summary: 2/5 services configured
```

---

## Step 5: Run Your First Query

```bash
# Test with Google DNS IP
poetry run threatfusion enrich 8.8.8.8
```

**You should see:**
1. ✅ Indicator validation
2. ✅ Agent initialization
3. ⏳ Parallel querying (5-30 seconds)
4. 📊 Risk score and results

---

## Quick Command Reference

```bash
# Enrich indicators
poetry run threatfusion enrich <HASH|IP|DOMAIN>

# JSON output
poetry run threatfusion enrich 8.8.8.8 --output json

# HTML report
poetry run threatfusion enrich malware.com --output html

# Save to file
poetry run threatfusion enrich <indicator> --save output.txt

# Configuration check
poetry run threatfusion config-check

# Version info
poetry run threatfusion version
```

---

## Example Queries

```bash
# IP address
poetry run threatfusion enrich 1.1.1.1

# Domain
poetry run threatfusion enrich example.com

# MD5 hash (EICAR test file)
poetry run threatfusion enrich 44d88612fea8a8f36de82e1278abb02f

# SHA256 hash
poetry run threatfusion enrich 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
```

---

## ⚠️ Common Issues

### "No module named 'click'"
```bash
# Solution: Install dependencies first
poetry install
```

### "ModuleNotFoundError: No module named 'src'"
```bash
# Solution: Always use 'poetry run'
poetry run threatfusion enrich 8.8.8.8
```

### "externally-managed-environment"
```bash
# Solution: DON'T use pip, use Poetry
poetry install  # ✅ Correct
pip install -r requirements.txt  # ❌ Wrong on Linux/WSL
```

### Can't see `.env` file
```bash
# Solution: Show hidden files
ls -a
```

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## What's Next?

- **Read the full docs**: [README.md](README.md)
- **Understand the architecture**: Check `src/` folder structure
- **Run tests**: `poetry run pytest tests/`
- **Customize configuration**: Edit `.env` file parameters

---

## Pro Tips

💡 **Create an alias** for easier usage:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias tf='poetry run threatfusion'

# Now you can just type:
tf enrich 8.8.8.8
```

💡 **Enter Poetry shell** for multiple commands:
```bash
poetry shell
# Now run without 'poetry run' prefix:
threatfusion enrich 8.8.8.8
threatfusion config-check
```

💡 **Batch analysis** (coming soon):
```bash
poetry run threatfusion batch indicators.txt
```

---

**Need Help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub!
