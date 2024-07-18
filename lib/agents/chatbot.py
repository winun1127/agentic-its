from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from lib.config import FAST_LLM
from lib.prompts import TEST_PROMPT

      
# ----------------------------------------------------------------------
# Chatbot
# ----------------------------------------------------------------------
class Chatbot:
    def __init__(self, model=FAST_LLM, system_prompt=TEST_PROMPT):
        self.model = model
        self.system_prompt = system_prompt
        
        self.main_chain = (
            ChatPromptTemplate.from_template(self.system_prompt)
            | ChatOpenAI(model=self.model) 
            | StrOutputParser()
        )
    
    # --------------------------------------------------
    # Interface
    # --------------------------------------------------
    def get_response(self, input_dict, streaming=False):
        if streaming:
            return self.main_chain.stream(input_dict)
        else: 
            response = self.main_chain.invoke(input_dict)
            return response

