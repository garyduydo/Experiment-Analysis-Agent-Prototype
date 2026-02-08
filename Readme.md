#  Experiment Analyzer - Hybrid Mode

AI-powered A/B test analysis tool with hybrid API key support and automatic key rotation.

##  Features

- **Hybrid Key Mode**: Use server keys OR let users provide their own
- **Key Rotation**: Automatically rotate between multiple API keys
- **Instant Analysis**: Get expert-level insights in seconds
- **100% Free**: Powered by Groq's free API
- **Beautiful UI**: Cyberpunk-themed interface

## 🚀 Quick Start

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env
# Edit .env and add your Groq API key

# 3. Run the server
python api.py

# 4. Visit http://localhost:5000
```

### Environment Setup

Create `.env` file:

```bash
GROQ_API_KEY=gsk_your_key_here
GROQ_API_KEY_2=gsk_another_key_here  # Optional
PORT=5000
```

Get free keys at: https://console.groq.com

##  Usage

**Server Key Mode**: Just visit and start analyzing
**Own Key Mode**: Toggle switch and enter your Groq key

Upload JSON or use sample data to analyze experiments.

##  Key Rotation

Add multiple keys for automatic rotation:
```bash
GROQ_API_KEY=gsk_key1
GROQ_API_KEY_2=gsk_key2
GROQ_API_KEY_3=gsk_key3
```

Benefits: 3x rate limits, load balancing, redundancy

##  Files

- `api.py` - Hybrid Flask backend
- `index.html` - React frontend
- `requirements.txt` - Dependencies
- `Render.yaml` - Deploy config

##  Troubleshooting

**No API key**: Set `GROQ_API_KEY` or use own key
**400 Error**: Check key is valid (starts with gsk_)
**Port in use**: Change PORT in .env

## 📝 License

MIT - Use freely!

---
