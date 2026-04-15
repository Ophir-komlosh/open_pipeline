import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = "https://api.openai.com/v1"

with open("SYSTEM_PROMPT.md", "r") as f:
    SYSTEM_PROMPT = f.read()

VERSION_PREFIX = "/v1"
COMPLETIONS_PATH = "/chat/completions"
FULL_PATH = VERSION_PREFIX + COMPLETIONS_PATH

AUTH_HEADER = "Authorization"
AUTH_PROMPT = f"Bearer {OPENAI_API_KEY}"

CONTENT_TYPE_HEADER = "Content-Type"
CONTENT_TYPE_PROMPT = "application/json"
