""" This module is responsible for loading external document.
"""
from langchain.document_loaders import DirectoryLoader

class LangchainDocumentLoader():
    """ This class is responsible for loading external document
    """

    def __init__(
            self,
            directory_path,
            glob
    ):
        self._loader = DirectoryLoader(directory_path, glob=glob and "**/*.pdf")

    def execute(
            self,
    ):
        """ This method is loading external document.
        :return: Any
        """
        data = self._loader.load()
        return data
