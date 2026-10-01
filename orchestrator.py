"""
Orchestrator — drives the multi-step architecture advisory pipeline.

Pipeline
--------
1. Gather requirements from the user (or accept them as a dict).
2. Score candidate architectures with the Gemini model.
3. Pick the best combination and produce a human-readable explanation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from google import genai

from config import GEMINI_API_KEY

# ── Configure Gemini ──────────────────────────────────────────────────────────
_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
_MODEL = "gemini-2.5-flash"

# ── Candidate dimensions ──────────────────────────────────────────────────────
ARCHITECTURES = [
    "Microservices",
    "Monolith",
    "Serverless",
    "Event-Driven",
    "Micro-Frontend",
    "Hexagonal (Ports & Adapters)",
]

CLOUDS = ["AWS", "GCP", "Azure", "Multi-Cloud", "On-Premise"]

DEPLOYMENTS = ["Kubernetes", "Docker Compose", "Serverless Functions", "VM / Bare-Metal", "PaaS (Heroku / Railway)"]


# ── Internal helpers ──────────────────────────────────────────────────────────
def _ask(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    response = _CLIENT.models.generate_content(model=_MODEL, contents=prompt)
    return (response.text or "").strip()


def _extract_json(text: str) -> dict:
    """
    Pull the first JSON object out of a model response.
    Gemini sometimes wraps JSON in markdown fences — strip them first.
    """
    # Remove ``` fences
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()

    # Grab the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model response:\n{text}")
    return json.loads(match.group())


# ── Public entry point ────────────────────────────────────────────────────────
def run_agent(requirements: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Run the architecture advisory pipeline.

    Parameters
    ----------
    requirements:
        Optional pre-filled requirements dict with keys:
        ``project_type``, ``scale``, ``team_size``, ``budget``,
        ``latency_sensitivity``, ``compliance``.
        When *None*, sensible defaults are used so the agent can run
        without interactive input.

    Returns
    -------
    dict with keys:
        architecture, cloud, deployment, scores, explanation
    """
    if requirements is None:
        requirements = _default_requirements()

    req_text = _format_requirements(requirements)

    # ── Step 1: score every combination ──────────────────────────────────────
    scoring_prompt = f"""
You are a senior software architect. A client described their project:

{req_text}

Candidate options:
  Architectures : {ARCHITECTURES}
  Clouds        : {CLOUDS}
  Deployments   : {DEPLOYMENTS}

Score EACH option 0–10 for this specific project.
Return ONLY valid JSON in exactly this shape (no prose, no fences):
{{
  "architectures": {{"Microservices": 7, "Monolith": 5, ...}},
  "clouds":        {{"AWS": 8, "GCP": 7, ...}},
  "deployments":   {{"Kubernetes": 9, "Docker Compose": 6, ...}}
}}
""".strip()

    raw_scores = _ask(scoring_prompt)
    scores = _extract_json(raw_scores)

    # ── Step 2: pick the best ─────────────────────────────────────────────────
    best_arch   = max(scores["architectures"],  key=scores["architectures"].get)
    best_cloud  = max(scores["clouds"],         key=scores["clouds"].get)
    best_deploy = max(scores["deployments"],    key=scores["deployments"].get)

    # ── Step 3: generate explanation ──────────────────────────────────────────
    explain_prompt = f"""
You are a senior software architect writing a concise advisory report.

Project requirements:
{req_text}

Recommended stack:
  Architecture : {best_arch}
  Cloud        : {best_cloud}
  Deployment   : {best_deploy}

Write 3–5 sentences explaining WHY this combination is the best fit,
including any important trade-offs the team should be aware of.
Write in plain English — no markdown, no bullet lists.
""".strip()

    explanation = _ask(explain_prompt)

    return {
        "architecture": best_arch,
        "cloud":        best_cloud,
        "deployment":   best_deploy,
        "scores":       scores,
        "explanation":  explanation,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def _default_requirements() -> dict:
    return {
        "project_type":       "SaaS web application",
        "scale":              "medium (10k–100k users)",
        "team_size":          "5–10 engineers",
        "budget":             "moderate",
        "latency_sensitivity": "medium",
        "compliance":         "GDPR",
    }


def _format_requirements(req: dict) -> str:
    lines = []
    for k, v in req.items():
        key = k.replace("_", " ").title()
        lines.append(f"  {key}: {v}")
    return "\n".join(lines)
