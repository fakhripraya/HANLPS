""" Environment Variable
"""

import os

INSECURE_PORT = str(os.getenv("INSECURE_PORT"))
LLM_USED = str(os.getenv("LLM_USED"))
USE_MODULE = str(os.getenv("USE_MODULE"))
GEMINI_MODEL = str(os.getenv("GEMINI_MODEL"))
GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))
HUGGINGFACE_MODEL = str(os.getenv("HUGGINGFACE_MODEL"))
OPENAI_MODEL = str(os.getenv("OPENAI_MODEL"))
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))
ADVERTISING_PIC_NUMBER = str(os.getenv("ADVERTISING_PIC_NUMBER"))
SERVICE_PIC_NUMBER = str(os.getenv("SERVICE_PIC_NUMBER"))
DEVELOPMENT_STATE = str(os.getenv("DEVELOPMENT_STATE"))