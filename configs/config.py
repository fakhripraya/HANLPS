""" Environment Variable
"""

import os
from dotenv import load_dotenv

load_dotenv()

INSECURE_PORT = str(os.getenv("INSECURE_PORT"))