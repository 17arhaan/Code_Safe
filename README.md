# Code Safe 🛡️

**AI-Powered Security Vulnerability Scanner for Python Codebases**

Code Safe leverages the power of Large Language Models (LLMs) to automatically discover complex, multi-step security vulnerabilities that traditional static analysis tools miss.

**Author:** [Arhaan Girdhar](https://github.com/17arhaan)  
**Repository:** [https://github.com/17arhaan/Code_Safe](https://github.com/17arhaan/Code_Safe)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for web UI)
- OpenAI API key or Anthropic API key

### Installation

1. **Clone and setup:**
```bash
git clone https://github.com/17arhaan/Code_Safe.git
cd Code_Safe
pip install -e .
```

2. **Configure API keys:**
```bash
# Copy your API keys to .env file
cp .env.example .env
# Edit .env with your actual API keys
```

3. **Run the backend:**
```bash
# Analyze a project
code_safe -r /path/to/your/project -l gpt

# Get help
code_safe --help
```

4. **Run the frontend (optional):**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## 📁 Project Structure

```
Code_Safe/
├── backend/              # Python CLI tool
│   ├── __main__.py      # Main entry point
│   ├── LLMs.py          # AI model integrations
│   ├── prompts.py       # Analysis prompts
│   └── symbol_finder.py # Code analysis engine
├── frontend/            # Next.js web interface
│   └── src/            # React components
├── .env                # API keys (create from .env.example)
├── pyproject.toml      # Python dependencies
└── Dockerfile          # Container support
```

## 🔍 Supported Vulnerabilities

- **🔴 Remote Code Execution (RCE)** - Arbitrary code execution
- **🟠 Local File Inclusion (LFI)** - Unauthorized file access
- **🟡 Cross-Site Scripting (XSS)** - Client-side code injection
- **🟣 SQL Injection (SQLI)** - Database attacks
- **🔵 Server-Side Request Forgery (SSRF)** - Internal network access
- **🩷 Arbitrary File Overwrite (AFO)** - File system manipulation
- **🟢 Insecure Direct Object Reference (IDOR)** - Access control bypass

## 💻 Usage Examples

### Command Line Interface
```bash
# Analyze entire project
code_safe -r /path/to/project

# Analyze specific file
code_safe -r /path/to/project -a app.py

# Use Claude instead of GPT
code_safe -r /path/to/project -l claude

# Verbose output
code_safe -r /path/to/project -v
```

### Docker
```bash
# Build image
docker build -t code_safe:local .

# Run analysis
docker run --rm -v /path/to/project:/repo code_safe:local -r /repo
```

## ⚙️ Configuration

Create a `.env` file with your API keys:

```bash
# Required: At least one API key
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Model configuration
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

## 📊 Sample Output

```
Analyzing /project/app.py
----------------------------------------

analysis:
  Critical Remote Code Execution vulnerability in /exec endpoint.
  User input passed directly to subprocess.run() without sanitization...

poc:
  GET /exec?cmd=whoami

confidence_score: 9

vulnerability_types:
  - RCE
```

## 🎯 Confidence Scores

- **0-6**: Low confidence, likely false positive
- **7**: Medium confidence, worth investigating  
- **8-10**: High confidence, very likely genuine vulnerability

## ⚠️ Important Notes

- **Monitor API Costs**: Analysis uses AI tokens - set spending limits
- **Python 3.10+ Required**: For Jedi dependency compatibility
- **Rate Limits**: Be mindful of API rate limits on large projects
- **Security**: Never commit `.env` file with API keys

## 🤝 Contributing

This is your personal security analysis tool. Feel free to:
- Add new vulnerability detection patterns
- Improve LLM prompts for better accuracy
- Add support for additional programming languages
- Enhance the reporting format

## 👨‍💻 Author

**Arhaan Girdhar**  
- GitHub: [@17arhaan](https://github.com/17arhaan)
- Project Repository: [Code_Safe](https://github.com/17arhaan/Code_Safe)

## 📝 License

This project is for personal use and security research purposes.

---

**Happy Bug Hunting! 🐛🔍**

*Built with ❤️ by [Arhaan Girdhar](https://github.com/17arhaan)*