""" Module for PromptParser class."""

from typing import Any
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel

class PromptParser():
    """ PromptParser class.
    """
    def __init__(self, llm_client: ChatOpenAI):
        self._client = llm_client

    def execute(self, input: dict, templates: dict[list[str], Any]) -> str:
        """ Parse the incoming prompt.
        :param prompt: Prompt to be parse.
        :return: output
        """
        
        runnable = None
        temp_analysis_prompt = None
        composed_chain = None
        count = 0
        for template in templates:
            if runnable is None:
                temp_analysis_prompt: ChatPromptTemplate = template
                composed_chain = temp_analysis_prompt.pipe(self._client).pipe(StrOutputParser())
            else:
                composed_chain = runnable.pipe(temp_analysis_prompt).pipe(self._client).pipe(StrOutputParser())
            count += 1
            
            if count is not len(templates):
                runnable = RunnableParallel({"prompts": composed_chain})
            else:
                break
            
        runnable_output = composed_chain.invoke(input)
        return runnable_output
        