"""Paths and settings, read from environment variables (and a local .env file)."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

PDF_PATH = PROJECT_ROOT / "docs" / "raw-document" / "FIA 2026 F1 Regulations Section B.pdf"
DATA_DIR = PROJECT_ROOT / "data"
PROVISIONS_FILE = DATA_DIR / "parsed" / "provisions.json"
TERMS_FILE = DATA_DIR / "parsed" / "terms.json"
VOCAB_FILE = DATA_DIR / "entities" / "vocab.json"
EXTRACTIONS_DIR = DATA_DIR / "entities" / "extractions"
EVAL_DIR = DATA_DIR / "eval"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_ANSWER_MODEL = os.getenv("GROQ_ANSWER_MODEL", "openai/gpt-oss-120b")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Local embedding model (runs on CPU) and the size of the vectors it produces.
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384
