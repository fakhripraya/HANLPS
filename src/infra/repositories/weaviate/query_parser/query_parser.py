""" Module for QueryParser class."""

from src.interactor.interfaces.repositories.weaviate.query_parser import QueryParserInterface

class QueryParser(QueryParserInterface):
    """ QueryParser class.
    """

    def execute(self , dict) -> str:
        """ Parse the incoming query.
        :return: output
        """
        output = ""

        key_prefix_pairs = {
            "building_title": "",
            "building_address": "Terletak di: ",
            "building_proximity": "Dekat dengan: ",
            "building_facility": "Memiliki fasilitas: "
        }

        for index, (key, prefix) in enumerate(key_prefix_pairs.items()):
            if dict.get(key):
                if index > 0:
                    output += " "
                output += prefix + dict[key]

        return output
        
        