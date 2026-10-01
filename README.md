# ArchMind — AI Architecture Advisor

Gemini-powered architecture advisor that scores and recommends the best
architecture, cloud, and deployment strategy for your project.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your Gemini API key
cp .env.example .env
# edit .env → set GEMINI_API_KEY=your_key_here

# 3a. Run the CLI
python main.py

# 3b. Start the web server + UI
python main.py --serve
# open http://localhost:5000
```

## Bugs fixed from v1
| File | Problem | Fix |
|------|---------|-----|
| `.env` | Key named `OPENAI_API_KEY` but code reads `GEMINI_API_KEY` | Renamed to `GEMINI_API_KEY` |
| `config.py` | Debug `print` of secret key | Removed |
| `agent/` | Directory didn't exist | Created `agent/orchestrator.py` + `__init__.py` |
| `main.py` | Imported non-existent module path | Corrected import; added `--serve` flag |
| — | No web server or frontend | Added `app.py` (Flask) + `static/index.html` |

## Project structure
```
arch_advisor/
├── .env                  ← your secrets (never commit)
├── config.py             ← loads & validates env vars
├── main.py               ← CLI + server entry point
├── app.py                ← Flask REST API
├── requirements.txt
├── agent/
│   ├── __init__.py
│   └── orchestrator.py   ← Gemini pipeline
└── static/
    └── index.html        ← frontend UI
```
