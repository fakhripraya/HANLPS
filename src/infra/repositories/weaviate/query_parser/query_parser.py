""" Module for QueryParser class."""

from typing import Any

class QueryParser():
    """ QueryParser class.
    """

    def execute(self , dict: dict[str, Any]) -> str:
        """ Parse the incoming query.
        :return: parsed_query
        """
        parsed_query = ""

        key_prefix_pairs = {
            "building_title": "",
            "building_address": "Beralamat di ",
            "building_proximity": "Dekat dengan ",
            "building_facility": "Memiliki fasilitas",
            "building_note": "",
        }

        for index, (key, prefix) in enumerate(key_prefix_pairs.items()):
            if dict.get(key):
                if index > 0:
                    parsed_query += " "
                parsed_query += prefix + dict[key]

        return parsed_query
        
        