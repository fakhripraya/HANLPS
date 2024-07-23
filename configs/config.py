""" Environment Variable
"""

import os

IN_DEVELOPMENT = bool(str(os.getenv("IN_DEVELOPMENT")))
INSECURE_PORT = str(os.getenv("INSECURE_PORT"))

LLM_USED = str(os.getenv("LLM_USED"))
USE_MODULE = str(os.getenv("USE_MODULE"))
MODULE_USED = str(os.getenv("MODULE_USED"))

GEMINI_MODEL = str(os.getenv("GEMINI_MODEL"))
GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))

HUGGINGFACE_MODEL = str(os.getenv("HUGGINGFACE_MODEL"))

OPENAI_MODEL = str(os.getenv("OPENAI_MODEL"))
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))
OPENAI_ORGANIZATION_ID = str(os.getenv("OPENAI_ORGANIZATION_ID"))

ADVERTISING_PIC_NUMBER = str(os.getenv("ADVERTISING_PIC_NUMBER"))
SERVICE_PIC_NUMBER = str(os.getenv("SERVICE_PIC_NUMBER"))