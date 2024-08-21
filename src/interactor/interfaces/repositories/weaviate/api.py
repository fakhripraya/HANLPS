""" Module provides a weaviate API interface.
"""

import weaviate as weaviate_lib
from abc import ABC, abstractmethod

class WeaviateAPIInterface(ABC):
    """ WeaviateAPIInterface class provides an interface for weaviate API.
    """
    
    @abstractmethod
    def connect_to_server(self, with_modules: int, module_used: str)  -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance locally
        """
    
    @abstractmethod
    def connect_locally(self) -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance locally
        """
    
    @abstractmethod
    def connect_with_openai(self) -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance with openai module
        """
    
    @abstractmethod
    def connect_with_google(self) -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance with google module
        """
    
    @abstractmethod
    def load_buildings_from_document_csv(self) -> None:
        """ 
        Load and insert new objects of building and insert it to db from document csv
        """
    
    @abstractmethod
    def load_buildings_from_document_json(self) -> None:
        """ 
        Load and insert new objects of building and insert it to db from json document
        """
        
    @abstractmethod
    def load_data_to_db(self, docs: list[dict]) -> None:
        """ 
        Insert a list of data to weaviate from documents
        """
    
    @abstractmethod
    def close_connection_to_server(self) -> None:
        """Close the connection to Weaviate server"""