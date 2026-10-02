# ArchMind — LLM Architecture Advisor

ArchMind recommends a software architecture, cloud provider and deployment target for a project.
It describes the project to Google Gemini, has the model score every candidate option, picks the
highest-scoring combination and writes a short advisory explaining the trade-offs.

Available as a **CLI** and as a **Flask REST API with a web UI**.

## How it works

```
requirements ──► scoring prompt ──► Gemini ──► JSON scores ──► pick best per dimension ──► explanation prompt ──► Gemini ──► report
```

1. **Requirements:** project type, scale, team size, budget, latency sensitivity and compliance
   (sensible defaults are used if none are given).
2. **Scoring:** Gemini (`gemini-2.5-flash`) scores every option 0–10 and is instructed to return
   JSON only:
   - 6 architectures: Microservices, Monolith, Serverless, Event-Driven, Micro-Frontend, Hexagonal
   - 5 clouds: AWS, GCP, Azure, Multi-Cloud, On-Premise
   - 5 deployment targets: Kubernetes, Docker Compose, Serverless Functions, VM / Bare-Metal, PaaS
3. **Defensive parsing:** LLM output is not always clean, so the parser strips markdown fences and
   extracts the first JSON object before using it, failing with a clear error if none is found.
4. **Selection + explanation:** the top-scoring option in each dimension is chosen and a second
   prompt produces a 3–5 sentence plain-English rationale, including trade-offs.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # then set GEMINI_API_KEY in .env
```

The key is read from the environment by `config.py`; `.env` is git-ignored and never committed.

## Usage

```bash
python main.py                # CLI: runs with default requirements and prints the report
python main.py --serve        # web UI + API at http://localhost:5000
```

### API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Liveness probe |
| `POST` | `/api/analyze` | Body: requirements JSON → recommendation, all scores and explanation |

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"project_type": "fintech API", "scale": "100k+ users", "team_size": "4 engineers",
       "budget": "tight", "latency_sensitivity": "high", "compliance": "PCI-DSS"}'
```

Unknown keys in the request body are ignored, so only the six expected fields reach the prompt.

## Project structure

```
archmind/
├── main.py           CLI and server entry point (--serve)
├── app.py            standalone Flask app (same API)
├── orchestrator.py   Gemini pipeline: prompts, JSON extraction, selection
├── config.py         loads and validates GEMINI_API_KEY
├── static/index.html web UI
├── requirements.txt
└── .env.example
```

## Stack

Python · Google Gemini API (`google-genai`) · Flask · prompt engineering
