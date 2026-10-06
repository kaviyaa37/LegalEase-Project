from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "Missing required environment variable GEMINI_API_KEY. Copy .env.example to .env and add your Gemini API key."
    )

# Google retired gemini-1.5-pro; keep the model configurable via GEMINI_MODEL.
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
LOGO_PATH = str(PROJECT_ROOT / "Image" / "Logo.png")
WEB_LOGO_PATH = str(PROJECT_ROOT / "Image" / "inverseLogo.png")
FOOTER_TEXT = "LegalEase Inc. | contact@legalease.com | All Rights Reserved."
FONT_NAME = "Times New Roman"
