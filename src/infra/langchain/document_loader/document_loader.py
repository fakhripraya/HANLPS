""" This module is responsible for loading external document.
"""
from langchain_community.document_loaders import DirectoryLoader, TextLoader

class LangchainDocumentLoader():
    """ This class is responsible for loading external document
    """

    def __init__(
            self,
            extension,
            directory_path,
            glob
    ):
        loader = None
        if extension == "pdf":
            loader = DirectoryLoader(directory_path, glob=glob and "**/*.pdf")
        elif extension == "txt":
            loader = TextLoader(directory_path)

        self._loader = loader

    def execute(
            self,
    ):
        """ This method is loading external document.
        :return: Any
        """
        data = self._loader.load()
        return data
