""" Environment Variable
"""

import os
from dotenv import load_dotenv

load_dotenv()

INSECURE_PORT = os.getenv("INSECURE_PORT")