""" Environment Variable
"""

import os
from dotenv import load_dotenv

load_dotenv()

INSECURE_PORT = str(os.getenv("INSECURE_PORT"))
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))