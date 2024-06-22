""" Module provides a weaviate API interface.
"""

from abc import ABC, abstractmethod

class WeaviateAPIInterface(ABC):
    """ WeaviateAPIInterface class provides an interface for weaviate API.
    """
    
    @abstractmethod
    def create_new_messages_tenant(self, tenant: str) -> None:
        """ 
        Create new tenant for messages collection
        :param tenant: tenant name.
        """