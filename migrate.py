""" Function to migrate imported Weaviate collections to the instance
"""

from src.infra.repositories.weaviate.api import WeaviateAPI
from src.infra.logger.logger_default import LoggerDefault
from dotenv import load_dotenv

load_dotenv()
logger = LoggerDefault()
with WeaviateAPI(logger) as instance:
    instance.migrate_datas()
