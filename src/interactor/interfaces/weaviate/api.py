""" Module provides a weaviate API interface.
"""

from abc import ABC, abstractmethod

class WeaviateAPIInterface(ABC):
    """ WeaviateAPIInterface class provides an interface for weaviate API.
    """
    
    @abstractmethod
    def load_buildings_from_document_csv(self) -> None:
        """ 
        Load and insert new objects of building and insert it to db from document csv
        """