""" Module for QueryParser class."""

from typing import Any


class QueryParser:
    """QueryParser class."""

    def execute(
        self, dict: dict[str, Any], key_prefix_pairs: dict[str, str] | None = None
    ) -> str:
        """Parse the incoming dictionary into desirable query.
        :return: parsed_query
        """
        parsed_query = ""

        key_prefix_pairs_default = {
            "building_title": "Hunian ",
            "building_address": "Beralamat di ",
            "building_proximity": "Dekat dengan ",
            "building_facility": "Memiliki fasilitas ",
            "building_note": "",
        }

        key_prefix_pairs = (
            key_prefix_pairs if key_prefix_pairs else key_prefix_pairs_default
        )
        for _, (key, prefix) in enumerate(key_prefix_pairs.items()):
            if dict.get(key):
                parsed_query += prefix + dict[key]
                parsed_query += " "

        return parsed_query
