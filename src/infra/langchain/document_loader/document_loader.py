""" This module is responsible for loading external document.
"""
from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader
from langchain_core.documents import Document
from typing import List, Dict
import json

class LangchainDocumentLoader():
    """ This class is responsible for loading external document
    """

    def __init__(
            self,
            extension,
            directory_path,
            glob = "**/*.pdf"
    ):
        loader = None
        if extension == "pdf":
            loader = DirectoryLoader(directory_path, glob=glob)
        elif extension == "csv":
            loader = CSVLoader(
                directory_path,
                csv_args={
                    "delimiter": ",",
                    "quotechar": '"',
                    "fieldnames": [
                        "building_title",
                        "building_address",
                        "building_description",
                        "housing_price",
                        "owner_name",
                        "owner_whatsapp",
                        "owner_phone_number",
                        "owner_email",
                        "image_url"
                    ],
                })
        elif extension == "txt":
            loader = TextLoader(directory_path)

        self._loader = loader

    def execute(
            self,
    ):
        """ This method is to load external document.
        :return: Any
        """
        docs = self._loader.load()
        structured_docs = self.documents_to_structured(docs)
        return structured_docs
    
    def parse_document(self, doc: Document) -> Dict:
        """ This method is to parse Document object into structured data.
        :param: Document: a single object of Document
        :return: Dict
        """
        # Split the page content by lines and then by ': ' to get key-value pairs
        lines = doc.page_content.split('\n')
        data = {}
        for line in lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                data[key] = value
        # Include metadata if needed
        data.update(doc.metadata)
        return data

    def documents_to_structured(self, docs: List[Document]) -> List[Dict]:
        """ This method is loading external document.
        :return: List[Dict]
        """
        # Parse each document and convert to list of dictionaries
        structured_docs: List[Dict] = [self.parse_document(doc) for doc in docs]
        return structured_docs
