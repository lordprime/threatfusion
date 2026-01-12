# 🚨 ThreatFusion

**Automated Threat Intelligence Aggregator**

Quickly enrich malware hashes, IPs, and domains with intelligence from multiple sources in under 30 seconds.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 What is ThreatFusion?

ThreatFusion is a command-line tool that automates the tedious process of manually querying multiple threat intelligence platforms. Instead of spending 15+ minutes visiting VirusTotal, Shodan, Censys, and other services separately, get complete intelligence in one command.

**Before ThreatFusion:**
```
1. Visit VirusTotal → Search → Wait
2. Visit Shodan → Search → Wait
3. Visit Censys → Search → Wait
4. Visit AlienVault OTX → Search → Wait
⏱️ Total: 15-30 minutes
```

**With ThreatFusion:**
```bash
$ threatfusion enrich abc123def456
✅ Complete intelligence in <30 seconds
```

---

## ✨ Features

- ⚡ **Parallel Queries**: Query 5+ APIs simultaneously
- 🎯 **Smart Detection**: Automatically detects indicator type (hash, IP, domain)
- 📊 **Risk Scoring**: Unified 0-10 risk score from all sources
- 📝 **Multiple Formats**: Text, JSON, and HTML reports
- 🔒 **Rate Limiting**: Built-in rate limiting for free tier APIs
- 🚦 **Progress Tracking**: Real-time progress indicators
- 🎨 **Beautiful Output**: Rich terminal formatting

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/threatfusion.git
cd threatfusion

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys
```

---

## 🔑 API Keys

ThreatFusion requires API keys from threat intelligence services. All services offer free tiers:

| Service | Free Tier | Sign Up |
|---------|-----------|---------|
| **VirusTotal** | 500 requests/day | [virustotal.com](https://www.virustotal.com) |
| **Shodan** | 100 queries/month | [shodan.io](https://www.shodan.io) |
| **Censys** | 250 queries/month | [censys.io](https://search.censys.io) |
| **AlienVault OTX** | Unlimited | [otx.alienvault.com](https://otx.alienvault.com) |
| **AbuseIPDB** | 1,000 checks/day | [abuseipdb.com](https://www.abuseipdb.com) |

### Configuration

Edit `.env` file:
```bash
VT_API_KEY=your_virustotal_api_key
SHODAN_API_KEY=your_shodan_api_key
CENSYS_API_ID=your_censys_id
CENSYS_API_SECRET=your_censys_secret
OTX_API_KEY=your_otx_api_key
ABUSEIPDB_API_KEY=your_abuseipdb_api_key
```

---

## 💻 Usage

### Basic Enrichment

```bash
# Enrich a malware hash
threatfusion enrich d131dd02c5e6eec4693d61a8d9ca3759

# Enrich an IP address
threatfusion enrich 192.168.1.1

# Enrich a domain
threatfusion enrich malicious-domain.com
```

### Output Formats

```bash
# JSON output
threatfusion enrich 8.8.8.8 --output json

# HTML report
threatfusion enrich malware.com --output html

# Save to file
threatfusion enrich abc123 --save report.html
```

### Configuration Check

```bash
# Check which API keys are configured
threatfusion config-check
```

---

## 📊 Example Output

```
================================================================================
THREATFUSION ENRICHMENT REPORT
================================================================================

Indicator: d131dd02c5e6eec4693d61a8d9ca3759
Analysis Time: 12.43s

RISK SCORE: 🔴 8.5/10 (CRITICAL)
Confidence: 90%

RISK COMPONENTS:
  • VirusTotal: 4.5/5 - 45/71 engines flagged as malicious
  • OTX: 2.0/2 - 12 threat intelligence pulses
  • AbuseIPDB: 0.8/1 - 80% abuse confidence

SOURCE RESULTS:
--------------------------------------------------------------------------------

VirusTotal:
  Detection Ratio: 45/71
  Malware Names: Trojan.Win32.Emotet, W32/Emotet, TrojanDownloader:Win32/Emotet

Shodan:
  Country: Russian Federation
  Organization: Hosting Provider LLC
  Vulnerabilities: 3 found

OTX:
  Threat Pulses: 12
  Has Threat Intel: Yes

================================================================================
```

---

## 🏗️ Architecture

```
ThreatFusion Architecture

┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                        │
│                    (Click + Rich Console)                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  Indicator Validator                        │
│            (Regex-based type detection)                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              Enrichment Orchestrator                        │
│           (ThreadPoolExecutor - Parallel)                   │
└┬────────┬────────┬────────┬────────┬─────────────────────────┘
 │        │        │        │        │
 ▼        ▼        ▼        ▼        ▼
[VT]   [Shodan] [Censys]  [OTX] [AbuseIPDB]
 │        │        │        │        │
 └────────┴────────┴────────┴────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Risk Scorer                              │
│          (Weighted multi-source analysis)                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                 Report Generator                            │
│              (Text / JSON / HTML)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=src tests/

# Run specific test
poetry run pytest tests/test_validators.py
```

---

## 🚀 Roadmap

- [ ] Additional agents (URLhaus, Talos Intelligence)
- [ ] Caching layer (SQLite) to reduce API calls
- [ ] Bulk analysis (CSV input)
- [ ] PDF report generation
- [ ] STIX 2.1 export format
- [ ] Web dashboard (FastAPI + React)

---

## ⚠️ Limitations

**Current MVP limitations:**

- **No caching**: Repeated queries re-fetch data (caching layer planned)
- **Free tier limits**: API quotas apply (VirusTotal: 500/day, Shodan: 100/month)
- **Basic normalization**: Different sources use different malware naming
- **Single user**: Not optimized for concurrent multi-user scenarios

These are acknowledged limitations of the MVP. Production enhancements are documented in the roadmap.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **VirusTotal** - File and URL analysis
- **Shodan** - Infrastructure intelligence
- **Censys** - Internet-wide scanning
- **AlienVault OTX** - Community threat intelligence
- **AbuseIPDB** - IP reputation

---

## 📧 Contact

**Author**: Abhishek Reddy
**Email**:hp2003r@gmail.com
**GitHub**: [@lordprime](https://github.com/lordprime)

---

**Built with ❤️ for security analysts who deserve better tools**
