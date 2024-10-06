""" This module is responsible for document text splitter.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter


class LangchainTextSplitter:
    """This class is responsible for splitting document that has been loaded into chunks"""

    def __init__(self, chunk_size, chunk_overlap):
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def execute(self, data):
        """This method is to split the document text.
        :param data: The input data transfer object.
        :type data: Any
        :return: Any
        """
        docs = self._text_splitter.split_documents(data)
        return docs
