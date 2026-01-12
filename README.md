# 🔍 ThreatFusion

**Automated Threat Intelligence Aggregator**

ThreatFusion is a powerful threat intelligence tool that enriches indicators (hashes, IPs, domains) with intelligence from multiple security sources including VirusTotal, Shodan, Censys, OTX, and AbuseIPDB.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ Features

- **🌐 Modern Web Dashboard**: Beautiful dark-themed UI with real-time analysis
- **⌨️ CLI Interface**: Powerful command-line tool for automation
- **Multi-Source Intelligence**: Aggregate data from 5+ threat intelligence APIs
- **Parallel Processing**: Query all sources simultaneously for fast results
- **Risk Scoring**: Automatic risk calculation with visual gauge
- **Multiple Output Formats**: Text, JSON, and HTML reports
- **Private IP Detection**: Warns when querying private/RFC1918 addresses
- **Rate Limiting**: Built-in rate limiting to respect API quotas

---

## 📋 Prerequisites

- **Python 3.11 or higher**
- **Poetry** (Python dependency manager)
- **API Keys** from at least one threat intelligence provider (see [API Keys](#-api-keys) section)

---

## 🚀 Installation

### Step 1: Install Poetry

If you don't have Poetry installed:

```bash
# Linux/WSL/macOS
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Verify installation:

## 1. Clone the repo

```
git clone https://github.com/lordprime/threatfusion.git
cd threatfusion
```
## 2. Install Python dependencies
```
poetry install
```
## 3. Install Frontend dependencies

```
cd frontend
npm install
cd ..
```
## 4. Configure API keys
```
cp .env.example .env
nano .env  # Add your API keys
```
# 5. Start both servers (in separate terminals)
```
# Terminal 1:
poetry run uvicorn api.main:app --reload --port 8000
# Terminal 2:
cd frontend && npm run deve
```
> [!TIP]
> You only need **at least one** API key to get started. More keys = more comprehensive results.

### Step 5: Verify Setup

```bash
poetry run threatfusion config-check
```

You should see a table showing which API services are configured.

---

## 🔑 API Keys

Register for free API keys at these providers:

| Provider | Free Tier | Registration Link |
|----------|-----------|-------------------|
| **VirusTotal** | 500 requests/day | [virustotal.com/gui/join-us](https://www.virustotal.com/gui/join-us) |
| **Shodan** | 100 results/month | [account.shodan.io/register](https://account.shodan.io/register) |
| **Censys** | 250 queries/month | [censys.io/register](https://censys.io/register) |
| **AlienVault OTX** | Unlimited (with registration) | [otx.alienvault.com/api](https://otx.alienvault.com/api) |
| **AbuseIPDB** | 1,000 checks/day | [abuseipdb.com/register](https://www.abuseipdb.com/register) |

---

## 🌐 Web Dashboard

The modern web interface provides a visual way to analyze threat indicators.

### Starting the Dashboard

**Terminal 1 - Start the API Server:**
```bash
poetry run uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Start the Frontend:**
```bash
cd frontend
npm run dev
```

**Open in Browser:** Navigate to `http://localhost:5173`

### Dashboard Features

- **Search Bar**: Enter IPs, domains, or file hashes
- **Risk Gauge**: Visual risk score from 0-10
- **Tabbed Results**: View results from each source (VirusTotal, Shodan, etc.)
- **Export**: Download reports as JSON or HTML
- **Config Status**: Check which API services are configured

---

## ⌨️ CLI Usage

### Basic Commands

```bash
# Enrich an IP address
poetry run threatfusion enrich 8.8.8.8

# Enrich a domain
poetry run threatfusion enrich malware.com

# Enrich a file hash (MD5/SHA1/SHA256)
poetry run threatfusion enrich 44d88612fea8a8f36de82e1278abb02f
```

### Output Formats

```bash
# Default: Rich terminal output with colors
poetry run threatfusion enrich 8.8.8.8

# JSON output
poetry run threatfusion enrich 8.8.8.8 --output json

# HTML report (auto-saved)
poetry run threatfusion enrich 8.8.8.8 --output html
```

### Advanced Options

```bash
# Save report to specific file
poetry run threatfusion enrich 8.8.8.8 --save report.json

# Increase timeout for slow connections
poetry run threatfusion enrich malware.com --timeout 60

# Check configuration
poetry run threatfusion config-check

# Show version info
poetry run threatfusion version
```

---

## 📊 Example Output

```
┌─────────────────────────────────────┐
│  🔍 ThreatFusion Analysis           │
├─────────────────────────────────────┤
│ Indicator: 8.8.8.8                  │
│ Type: ip_v4                         │
└─────────────────────────────────────┘

✓ Initialized 5 agents: VirusTotal, Shodan, Censys, OTX, AbuseIPDB

⠧ Querying 5 sources...

╔══════════════════════════════════════╗
║       RISK SCORE: 2.3 / 10.0        ║
║        Severity: LOW 🟢             ║
╚══════════════════════════════════════╝

Enrichment Results:
├─ VirusTotal: Clean (0/92 detections)
├─ Shodan: Google DNS, United States
├─ AbuseIPDB: Confidence 0%, Not malicious
└─ OTX: 3 pulses found
```

---

## 🛠️ Troubleshooting

### Common Issues

**❌ `externally-managed-environment` error**
- **Solution**: Use `poetry install` instead of `pip install`

**❌ `ModuleNotFoundError: No module named 'click'`**
- **Solution**: Run `poetry install` first, then use `poetry run threatfusion`

**❌ `ModuleNotFoundError: No module named 'src'`**
- **Solution**: Always use `poetry run threatfusion` or `poetry run python -m src.main`

**⚠️ Can't see `.env` file**
- **Solution**: Use `ls -a` to show hidden files

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## 📁 Project Structure

```
threatfusion/
├── src/
│   ├── agents/          # Threat intelligence agents
│   ├── clients/         # HTTP clients with rate limiting
│   ├── fusion/          # Orchestration and risk scoring
│   ├── reporting/       # Report generators
│   ├── config.py        # Configuration management
│   ├── models.py        # Data models
│   ├── validators.py    # Indicator validation
│   └── main.py          # CLI entry point
├── tests/               # Unit tests
├── examples/            # Example queries
├── .env.example         # Example configuration
├── pyproject.toml       # Poetry dependencies
├── README.md            # This file
├── QUICKSTART.md        # Quick setup guide
└── TROUBLESHOOTING.md   # Troubleshooting guide
```

---

## 🧪 Development

### Running Tests

```bash
poetry run pytest tests/
```

### Code Formatting

```bash
poetry run black src/
poetry run flake8 src/
```

### Type Checking

```bash
poetry run mypy src/
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

ThreatFusion is provided for educational and research purposes. Always ensure you have permission to query and analyze indicators. Respect API rate limits and terms of service for all integrated threat intelligence platforms.

---

## 🔗 Resources

- **Documentation**: [QUICKSTART.md](QUICKSTART.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/threatfusion/issues)

---

**Made with ❤️ by Security Researchers, for Security Researchers**
