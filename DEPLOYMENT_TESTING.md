# ThreatFusion GitHub Deployment & Testing Guide

## ✅ Completed Steps

1. Git repository initialized
2. All files committed (29 files, 2486+ lines)
3. GitHub remote added: https://github.com/lordprime/threatfusion

## 📤 Push to GitHub

Run this command to push your code:

```bash
git push -u origin main
```

> **Note**: GitHub may ask for authentication. Use a Personal Access Token (PAT) instead of password.

### Create GitHub Personal Access Token (if needed):
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Copy the token (you won't see it again!)
5. Use token as password when prompted

---

## 🧪 Testing ThreatFusion

### 1. Install Dependencies

```bash
cd d:\OSINT\threatfusion

# Using Poetry (recommended)
poetry install

# OR using pip
pip install -r requirements.txt
```

### 2. Configure API Keys

Create your `.env` file:

```bash
# Copy template
copy .env.example .env
```

Edit `.env` with your API keys:

```ini
VT_API_KEY=your_actual_virustotal_key
SHODAN_API_KEY=your_actual_shodan_key
CENSYS_API_ID=your_actual_censys_id
CENSYS_API_SECRET=your_actual_censys_secret
OTX_API_KEY=your_actual_otx_key
ABUSEIPDB_API_KEY=your_actual_abuseipdb_key
```

### 3. Verify Configuration

```bash
poetry run python src/main.py config-check
```

**Expected output:**
```
API Services Status
┌─────────────┬─────────────────┬─────────┐
│ Service     │ Status          │ Details │
├─────────────┼─────────────────┼─────────┤
│ VIRUSTOTAL  │ ✓ Configured    │ Ready   │
│ SHODAN      │ ✓ Configured    │ Ready   │
...
```

### 4. Test Queries

**Test 1: Known Malware Hash (EICAR test file)**
```bash
poetry run python src/main.py enrich 44d88612fea8a8f36de82e1278abb02f
```

**Expected**: High risk score (8-10), multiple detections

**Test 2: Clean IP (Google DNS)**
```bash
poetry run python src/main.py enrich 8.8.8.8
```

**Expected**: Low risk score (0-2), infrastructure info from Shodan

**Test 3: Domain**
```bash
poetry run python src/main.py enrich example.com
```

**Expected**: Low risk score, certificate info from Censys

### 5. Test Different Output Formats

```bash
# JSON output
poetry run python src/main.py enrich 8.8.8.8 --output json

# HTML report (auto-saved to file)
poetry run python src/main.py enrich 8.8.8.8 --output html
```

---

## 🔍 Validation Checklist

After testing, verify:

- [ ] All configured agents return data (check config-check)
- [ ] Risk scores are calculated correctly
- [ ] HTML reports are generated and viewable
- [ ] No Python errors or exceptions
- [ ] Execution time < 30 seconds per query
- [ ] Rate limiting works (no 429 errors immediately)

---

## 🐛 Troubleshooting

**Issue**: `ModuleNotFoundError`
```bash
# Solution: Install dependencies
poetry install
```

**Issue**: "No API keys configured"
```bash
# Solution: Check .env file exists and contains keys
dir .env
```

**Issue**: API returns 403/401
```bash
# Solution: Verify API key is correct
# Test key directly on API provider website
```

**Issue**: Rate limit errors (429)
```bash
# Solution: Wait a few minutes, free tiers reset
# Or add --timeout flag for slower execution
```

---

## 📊 Performance Benchmarks

**Expected performance:**

| Metric | Target | Actual |
|--------|--------|--------|
| Query Time | <30s | Test & record |
| Success Rate | >90% | Test & record |
| Memory Usage | <200MB | Monitor |
| Parallel Execution | 5 agents | Verify |

---

## 🎉 Success Criteria

Your ThreatFusion is working correctly if:

1. ✅ All API services show "✓ Configured"
2. ✅ Test queries complete without errors
3. ✅ Risk scores are calculated (0-10 scale)
4. ✅ Reports are generated in all formats
5. ✅ Execution completes in <30 seconds

---

## 📝 Next Steps After Testing

1. **Document results** in your portfolio
2. **Create demo video** showing enrichment
3. **Add screenshots** to README
4. **Share on LinkedIn** with #threatintelligence
5. **Apply to internships** with project link

---

## 🔗 Useful Commands Reference

```bash
# Check configuration
poetry run python src/main.py config-check

# Enrich indicator
poetry run python src/main.py enrich <indicator>

# Different outputs
poetry run python src/main.py enrich <indicator> --output json
poetry run python src/main.py enrich <indicator> --output html

# Run tests
poetry run pytest tests/ -v

# Check git status
git status

# View commit history
git log --oneline
```

---

**Ready to deploy and test!** 🚀
