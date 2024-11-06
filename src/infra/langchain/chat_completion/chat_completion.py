""" Module for ChatCompletion class."""

import json
from typing import Any
from src.infra.langchain.prompt_parser.prompt_parser import PromptParser
from langchain_core.prompts import ChatPromptTemplate


class ChatCompletion:
    """ChatCompletion class."""

    def execute(self, input: dict, parser: PromptParser, templates: list[str]) -> Any:
        """Execute the incoming prompt.
        :param input: Prompt to be parse and execute.
        :param parser: Prompt parser.
        :param templates: List of templates.
        :return: data_dict
        """

        chat_prompt_templates = self._mapTemplates(templates=templates)
        result: str = parser.execute(
            input,
            chat_prompt_templates,
        )
        result = result.strip("`").strip("json").strip("`").strip()
        data_dict = json.loads(result)

        return data_dict

    def _mapTemplates(self, templates: list[str]) -> list[ChatPromptTemplate]:
        chat_prompt_templates: list[ChatPromptTemplate] = []
        for template in templates:
            chat_prompt_templates.append(ChatPromptTemplate.from_template(template))

        return chat_prompt_templates
