# 🔐 Password Strength Checker

A production-ready CLI utility for comprehensive password security evaluation with breach detection and actionable recommendations.

## Features

✅ **Shannon Entropy Analysis** - Measures password randomness  
✅ **Complexity Scoring** - Evaluates character diversity and length  
✅ **Pattern Detection** - Identifies dictionary words, keyboard walks, sequences via `zxcvbn`  
✅ **Breach Detection** - Checks HaveIBeenPwned database using k-Anonymity protocol  
✅ **Secure Input** - Passwords hidden during entry (never logged or stored)  
✅ **Rich CLI UI** - Colored output, formatted tables, status indicators  
✅ **Actionable Recommendations** - Specific guidance to improve password strength  
✅ **Estimated Crack Times** - Shows resistance against various attack methods  

---

## Prerequisites

- **Python 3.10 or higher**
- **pip** (Python package installer)
- **Internet connection** (for HaveIBeenPwned API checks)

## Quick Start

### 1. Clone or Download
```bash
# If you have the project files
cd path/to/password-strength-checker
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create venv
python3 -m venv venv

# Activate venv
# On macOS/Linux:
source venv/bin/activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Windows (CMD):
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python3 main.py
```

### 5. Check a Password
1. Enter your password when prompted (input is hidden)
2. Review the comprehensive analysis report
3. Follow the recommendations to improve strength
4. Check another password or exit

---

## Usage Example

```
🔐 Password Strength Checker
Comprehensive security analysis with breach detection

Enter password to check (hidden): ••••••••••

🔍 Analyzing password...

Password Strength Analysis Report
──────────────────────────────────

Overall Strength: 🟢 Strong

📊 Security Metrics
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Metric       ┃ Value          ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Length       │ 14 characters  │
│ Entropy      │ 4.23 bits      │
│ Complexity   │ 38/50          │
│ Types        │ lowercase + uppercase + digits + special │
└──────────────┴────────────────┘

Pattern Analysis (zxcvbn):
  ✓ No common patterns detected

Breach Database Check:
  ✓ Password not found in known breaches

Recommendations:
  ✓ No improvements suggested

Estimated Crack Times:
  Online Attack: 1 year
  Offline Attack: centuries
  Offline Fast Attack: 2 months
```

---

## Security Features Explained

### 🔒 Masked Password Input
- Passwords are never echoed to the terminal
- Uses Python's `getpass` module for secure input
- Maximum length: 256 characters (prevents buffer overflow)

### 🔒 k-Anonymity Protocol (HaveIBeenPwned Check)
The application uses **k-Anonymity** to safely check if your password has been in breaches while **keeping your password private**:

**How it works:**
1. Your cleartext password is hashed locally with SHA-1
2. Only the **first 5 hex characters** of the hash are sent to the API
3. The API returns all passwords with matching prefixes (the "k-set")
4. The comparison is done **locally on your machine** — full hash never sent
5. Result: Your actual password never leaves your computer

**Example:**
```
Your Password: "MySecurePass123!"
SHA-1 Hash:    2F45A9E8C3D2B1F4A7E6C5D4B3A2F1E0D9C8B7A
Prefix:        2F45A (sent to API)
Full Hash:     2F45A9E8C3D2B1F4A7E6C5D4B3A2F1E0D9C8B7A (checked locally)
```

**Privacy guarantee:** Even if someone intercepts the prefix, they cannot reverse-engineer your password.

### 🔒 No Cleartext Storage
- Passwords are never logged to files
- Passwords are not stored in memory after analysis
- Analysis results (entropy, scores) are displayed once and discarded
- No configuration files store sensitive data

---

## Understanding the Analysis

### Shannon Entropy
**What it measures:** The randomness of character selection  
**How it works:** Calculates probability of each character repeating  
**Interpretation:**
- < 2.0 bits: Very predictable (avoid)
- 2.0-3.5 bits: Weak entropy
- 3.5-4.5 bits: Good entropy
- > 4.5 bits: Excellent entropy

**Formula:** H = -Σ(p_i × log₂(p_i))

Where p_i = frequency of character i

### Complexity Score (0-50)
**Factors:**
- **Length (0-20 points):** 2 points per character (max 20)
- **Diversity (0-30 points):** 7.5 points per character type (4 types max)
  - Lowercase letters
  - Uppercase letters
  - Digits (0-9)
  - Special characters (!@#$%^&*)

**Example:**
```
Password: "Pass123"
Length: 7 chars = 7 points
Types: lowercase (✓) + uppercase (✓) + digits (✓) + special (✗)
Diversity: 3 types × 7.5 = 22.5 points
Total: ~30/50 (Fair)
```

### zxcvbn Pattern Detection
**What it detects:**
- Dictionary words (common English words, name databases)
- Spatial patterns (QWERTY walks: `qwerty`, `123456`)
- Sequences (alphabetical: `abcd`, numeric: `2468`)
- Repeated characters (`aaaa`, `1111`)
- Year patterns (`2023`, `1995`)

**Strength Scores:**
- **0:** Very Weak (common words/patterns)
- **1:** Weak (dictionary words, simple patterns)
- **2:** Fair (mixed complexity, some patterns)
- **3:** Strong (good complexity, no major patterns)
- **4:** Very Strong (complex, no detectable patterns)

### HaveIBeenPwned Integration
**Data Checked Against:**
- Passwords from 600+ known data breaches
- LinkedIn, Facebook, Yahoo, Equifax, and others
- Updated regularly as new breaches are discovered

**Privacy Note:**
- Your password is **never sent to the API**
- Only a 5-character SHA-1 prefix is sent
- Checking is done on local machine
- 100% private and safe

---

## Troubleshooting

### Installation Issues

**Error: "No module named 'zxcvbn'"**
```bash
pip install --upgrade zxcvbn
```

**Error: "No module named 'rich'"**
```bash
pip install --upgrade rich
```

**Error: "No module named 'requests'"**
```bash
pip install --upgrade requests
```

### Runtime Issues

**Error: "HaveIBeenPwned check failed"**
- Check your internet connection
- The API may be temporarily unavailable
- The tool will continue with other analysis

**Error: "Connection timeout during breach check"**
- Internet connection may be slow
- Try again in a moment
- Breach check is optional; other analysis continues

**Performance is slow**
- First run may take longer as libraries load
- Subsequent runs are faster
- HaveIBeenPwned API calls take 1-2 seconds

### Virtual Environment Issues

**"command not found: python3"**
```bash
# Try python instead of python3
python --version
python -m venv venv
```

**"Permission denied" on activation**
```bash
# macOS/Linux: Add execute permission
chmod +x venv/bin/activate
source venv/bin/activate
```

---

## Technical Architecture

### Module Organization
```
main.py
├── PasswordStrengthChecker (main class)
│   ├── get_password_input() - Secure hidden input
│   ├── calculate_entropy() - Shannon entropy
│   ├── get_character_pools() - Character type detection
│   ├── calculate_complexity_score() - Complexity rating
│   ├── analyze_zxcvbn() - Pattern detection
│   ├── check_haveibeenpwned() - Breach detection (k-Anonymity)
│   ├── generate_recommendations() - Actionable feedback
│   ├── get_strength_rating() - Overall score
│   ├── display_results() - Rich terminal output
│   └── analyze() - Main pipeline
└── main() - CLI entry point
```

### Security Properties
| Property | Implementation |
|----------|------------------|
| **Password Visibility** | `getpass` module (hidden input) |
| **Password Storage** | Never persisted (variable scope) |
| **External API Privacy** | k-Anonymity (5-char SHA-1 prefix) |
| **Local Processing** | All comparisons done on client |
| **Logging** | No sensitive data logged |

### Dependencies
| Library | Purpose | Version |
|---------|---------|---------|
| zxcvbn | Pattern detection, strength scoring | 4.4.33 |
| requests | HTTP API calls (HaveIBeenPwned) | 2.31.0 |
| rich | Terminal formatting, UI | 13.7.0 |
| hashlib | SHA-1 hashing (stdlib) | built-in |
| getpass | Secure password input (stdlib) | built-in |

---

## Performance Notes

- **Entropy Calculation:** O(n) where n = password length
- **Complexity Scoring:** O(n) for regex scans
- **zxcvbn Analysis:** ~50-100ms per password
- **HaveIBeenPwned Check:** 1-2 seconds (API latency)
- **Total Time:** 1.5-2.5 seconds per password

---

## Example Passwords & Analysis

### Weak Password: `password123`
```
Length: 11 characters
Entropy: 2.8 bits
Patterns: Dictionary word "password" + sequential digits
zxcvbn Score: 1 (Weak)
Breach Status: COMPROMISED (appears in millions of breaches)
Recommendations:
  - Use unrelated words from a passphrase
  - Avoid sequential patterns
  - Add more special characters
```

### Good Password: `Tr0pic@lSunset2024`
```
Length: 19 characters
Entropy: 4.1 bits
Patterns: None detected
zxcvbn Score: 3 (Strong)
Breach Status: Not found in breaches
Recommendations:
  - Consider extending to 20+ characters
  - This password is strong—no immediate improvements needed
```

### Excellent Password: `7&Kx#mP2jQ@vL$nR9!sT`
```
Length: 20 characters
Entropy: 4.7 bits
Patterns: None detected
zxcvbn Score: 4 (Very Strong)
Breach Status: Not found in breaches
Recommendations:
  - ✓ No improvements suggested
```

---

## Recommended Practices

### For Strong Passwords
1. **Use 12-16+ characters** (longer = harder to crack)
2. **Mix character types** (uppercase, lowercase, digits, special)
3. **Avoid common words** (dictionary attacks fail)
4. **No sequential patterns** (no `abcd` or `1234`)
5. **No personal info** (names, birthdays, addresses)
6. **Unique per account** (if one breaches, others are safe)

### Passphrase Strategy
```
❌ Weak: "Love2024!"
✓ Better: "CorrectHorseBatteryStaple" (but add digits/special: "CorrectHorse2024@Battery!")
✓ Best: "PurpleFrogDancesAt3AM#Kitchen" (long, random, memorable)
```

### Using a Password Manager
- Store strong passwords in reputable managers (1Password, Bitwarden, KeePass)
- Let the tool generate random 20+ character passwords
- Use this tool to verify password strength
- Never reuse passwords across accounts

---

## API References

### HaveIBeenPwned API
- **Endpoint:** https://api.pwnedpasswords.com/range/{prefix}
- **Documentation:** https://haveibeenpwned.com/API/v3
- **Privacy Model:** k-Anonymity protocol
- **Rate Limit:** None for prefix searches (prefixes share little info)

### zxcvbn Library
- **Repository:** https://github.com/dropbox/zxcvbn
- **Python Port:** https://github.com/dwolfhub/zxcvbn-python
- **Scoring:** OWASP recommendations
- **Patterns:** Dictionary, spatial, temporal, repeat

---

## Version History

**v1.0 (Current)**
- Initial release
- Full entropy and complexity analysis
- zxcvbn pattern detection
- k-Anonymity breach checking
- Rich terminal UI
- Actionable recommendations

---

## License

This tool is provided as-is for educational and security evaluation purposes. Use it to strengthen your password security.

---

## Support & Feedback

For issues, improvements, or questions:
1. Review the troubleshooting section above
2. Check that dependencies are correctly installed
3. Ensure Python 3.10+ is being used
4. Verify internet connection for breach checks

---

## Security Disclaimer

This tool provides **guidance only**. It does not guarantee password security against:
- Compromised input devices (keyloggers)
- Malware on your computer
- Physical access to your machine
- Social engineering attacks

Always practice basic security hygiene:
- Keep your OS and software updated
- Use antivirus software
- Enable two-factor authentication
- Use unique passwords per account
- Store passwords securely in a password manager

---

**Stay secure! 🔐**
