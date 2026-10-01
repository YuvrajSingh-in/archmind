"""
main.py — Architecture Advisor

Usage
-----
  python main.py            # CLI
  python main.py --serve    # Web UI at http://localhost:5000
"""

import argparse
import sys
import traceback
from pathlib import Path

from orchestrator import run_agent


# ── CLI ────────────────────────────────────────────────────────────────────────
def run_cli() -> None:
    print("\n  Architecture Advisor - analysing your project...\n")
    result = run_agent()

    sep = "=" * 62
    print(sep)
    print("  RECOMMENDATION")
    print(sep)
    print(f"  Architecture : {result['architecture']}")
    print(f"  Cloud        : {result['cloud']}")
    print(f"  Deployment   : {result['deployment']}")
    print()
    print("  SCORES  (top 3 per dimension)")
    print("  " + "-" * 44)
    for dim, scores in result["scores"].items():
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        line   = ", ".join(f"{n} ({s})" for n, s in ranked)
        print(f"  {dim.capitalize():16}: {line}")
    print()
    print("  EXPLANATION")
    print("  " + "-" * 44)
    for line in result["explanation"].splitlines():
        print(f"  {line}")
    print(sep)


# ── Web server ─────────────────────────────────────────────────────────────────
def run_server() -> None:
    try:
        from flask import Flask, jsonify, request, send_from_directory
        from flask_cors import CORS
    except ImportError:
        sys.exit("Flask not installed. Run:  pip install flask flask-cors")

    STATIC = Path(__file__).parent / "static"
    app = Flask(__name__, static_folder=str(STATIC), static_url_path="")
    CORS(app)

    @app.get("/")
    def index():
        return send_from_directory(str(STATIC), "index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/api/analyze")
    def analyze():
        body    = request.get_json(silent=True) or {}
        allowed = {"project_type", "scale", "team_size",
                   "budget", "latency_sensitivity", "compliance"}
        reqs    = {k: v for k, v in body.items() if k in allowed} or None
        try:
            return jsonify({"ok": True,  "data": run_agent(reqs)})
        except Exception as exc:
            traceback.print_exc()
            return jsonify({"ok": False, "error": str(exc)}), 500

    print("Web UI ready at http://localhost:5000")
    app.run(debug=False, port=5000)


# ── Entry ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Architecture Advisor")
    parser.add_argument("--serve", action="store_true",
                        help="Launch the Flask web UI")
    args = parser.parse_args()
    run_server() if args.serve else run_cli()


if __name__ == "__main__":
    main()
