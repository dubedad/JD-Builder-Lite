"""Configuration constants for JD Builder Lite."""

import os

OASIS_BASE_URL = "https://noc.esdc.gc.ca"
OASIS_VERSION = "2025.0"
REQUEST_TIMEOUT = 60  # seconds
USER_AGENT = "JD-Builder-Lite/1.0 (Educational Demo)"

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 300  # ~4-6 sentences
OPENAI_TEMPERATURE = 0.7  # Balanced creativity

# Flask session
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")

# JobForge vocabulary source
JOBFORGE_BRONZE_PATH = "C:/Users/Administrator/Dropbox/++ Results Kit/JobForge 2.0/data/bronze"
