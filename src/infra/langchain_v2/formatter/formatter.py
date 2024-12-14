""" Module for JSONFormatter class."""

import json
from typing import Any


class JSONFormatter:
    """JSONFormatter class."""

    def execute(
        self,
        input: str,
    ) -> Any | str:
        """Format incoming input into JSON format.
        :param input: Prompt to be parse and execute.
        :return: Any | str
        """
        result = input.strip("`").strip("json").strip("`").strip()
        data_dict = json.loads(result)
        return data_dict
