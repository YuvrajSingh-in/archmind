"""
app.py — Flask REST API that wraps the architecture advisory agent.

Endpoints
---------
POST /api/analyze   Body: JSON requirements dict  →  advisory result
GET  /api/health    Liveness probe
GET  /              Serves the frontend
"""

from __future__ import annotations

import traceback
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from orchestrator import run_agent

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
CORS(app)


# ── Frontend ──────────────────────────────────────────────────────────────────
@app.get("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


# ── API ───────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/analyze")
def analyze():
    body = request.get_json(silent=True) or {}

    # Validate / normalise incoming keys
    allowed = {
        "project_type", "scale", "team_size",
        "budget", "latency_sensitivity", "compliance",
    }
    requirements = {k: v for k, v in body.items() if k in allowed} or None

    try:
        result = run_agent(requirements)
        return jsonify({"ok": True, "data": result})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(exc)}), 500


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False, port=5000)
