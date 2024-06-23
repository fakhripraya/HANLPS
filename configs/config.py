""" Environment Variable
"""

import os

INSECURE_PORT = str(os.getenv("INSECURE_PORT"))
OPENAI_MODEL = str(os.getenv("OPENAI_MODEL"))
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))
ADVERTISING_PIC_NUMBER = str(os.getenv("ADVERTISING_PIC_NUMBER"))
SERVICE_PIC_NUMBER = str(os.getenv("SERVICE_PIC_NUMBER"))