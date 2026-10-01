import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "❌ GEMINI_API_KEY not found.\n"
        "   → Create a .env file with: GEMINI_API_KEY=your_key_here\n"
        "   → Or export it: export GEMINI_API_KEY=your_key_here"
    )
