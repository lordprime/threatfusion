# 🚀 ThreatFusion Quick Start Guide

## Get Up and Running in 5 Minutes

### Step 1: Navigate to Project
```bash
cd d:\OSINT\threatfusion
```

### Step 2: Install Dependencies
```bash
# Install Poetry (if not installed)
pip install poetry

# Install project dependencies
poetry install
```

### Step 3: Configure API Keys

Copy the example configuration:
```bash
copy .env.example .env
```

Edit `.env` and add your API keys:
```ini
VT_API_KEY=your_virustotal_api_key_here
SHODAN_API_KEY=your_shodan_api_key_here
CENSYS_API_ID=your_censys_id_here
CENSYS_API_SECRET=your_censys_secret_here
OTX_API_KEY=your_otx_api_key_here
ABUSEIPDB_API_KEY=your_abuseipdb_api_key_here
```

> **Where to get API keys?** See [README.md](file:///d:/OSINT/threatfusion/README.md) for registration links

### Step 4: Verify Setup
```bash
poetry run python src/main.py config-check
```

### Step 5: Run Your First Query
```bash
# Test with EICAR test file hash
poetry run python src/main.py enrich 44d88612fea8a8f36de82e1278abb02f

# Or test with an IP
poetry run python src/main.py enrich 8.8.8.8

# Or test with a domain
poetry run python src/main.py enrich example.com
```

## Commands Reference

```bash
# Basic enrichment (text output)
poetry run python src/main.py enrich <indicator>

# JSON output
poetry run python src/main.py enrich <indicator> --output json

# HTML report (auto-saved)
poetry run python src/main.py enrich <indicator> --output html

# Check configuration
poetry run python src/main.py config-check

# Show version
poetry run python src/main.py version
```

## What to Expect

**Execution flow:**
1. Indicator validation (type detection)
2. Agent initialization (based on configured keys)
3. Parallel querying (5+ sources simultaneously)
4. Risk score calculation (0-10 scale)
5. Report generation (formatted output)

⏱️ **Total time:** <30 seconds for most queries

## Troubleshooting

**Issue: "No API keys configured"**
- Solution: Set up your `.env` file with API keys

**Issue: Rate limit errors**
- Solution: Some free tiers have daily limits (wait 24hrs or upgrade)

**Issue: Import errors**
- Solution: Run `poetry install` to ensure all dependencies are installed

## Next Steps

✅ **You're now ready to:**
- Query malware hashes, IPs, and domains
- Generate HTML reports for sharing
- Integrate into your security workflows

📖 **Read More:**
- [README.md](file:///d:/OSINT/threatfusion/README.md) - Full documentation
- [THREATFUSION_TECHNICAL_SETUP.md](file:///C:/Users/Abhi1/.gemini/antigravity/brain/3886f921-192e-4ddd-a08b-043709f6504d/THREATFUSION_TECHNICAL_SETUP.md) - Detailed setup
- [walkthrough.md](file:///C:/Users/Abhi1/.gemini/antigravity/brain/3886f921-192e-4ddd-a08b-043709f6504d/walkthrough.md) - Project overview
