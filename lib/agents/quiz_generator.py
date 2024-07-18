import glob
from typing import List
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SKLearnVectorStore

from langgraph.graph import StateGraph, START, END

from lib.config import FAST_LLM, LONG_CONTEXT_LLM
from lib.prompts import QUIZ_PROMPT
from lib.schema import Quiz

   
# ----------------------------------------------------------------------
# Quiz Generator
# ----------------------------------------------------------------------
class QuizGenerator:
    def __init__(self, model=LONG_CONTEXT_LLM, system_prompt=QUIZ_PROMPT):
        self.model = model
        self.system_prompt = system_prompt
        
        self.retriever = self._create_retriever()
        self.quiz_generator = self._create_quiz_generator()
        
        self.main_graph = self._create_main_graph()
        
        
    def _create_retriever(self):       
        pages = []
        pdf_files = glob.glob("docs/**/*.pdf", recursive=True)
        for file_path in pdf_files:
            loader = PyPDFLoader(file_path)
            pages.extend(loader.load_and_split())

        vectorstore = SKLearnVectorStore.from_documents(
            documents=pages,
            embedding=OpenAIEmbeddings(),
        )
        return vectorstore.as_retriever(k=4)
    
    
    def _create_quiz_generator(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("user", "{topic}"),
            ]
        )
        llm = ChatOpenAI(model=self.model)
        # return prompt | llm | StrOutputParser()
        return prompt | llm.with_structured_output(Quiz)
        
    # --------------------------------------------------
    # Graph
    # --------------------------------------------------    
    def _create_main_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("retrieve_docs", self.retrieve_docs)
        workflow.add_node("generate_quiz", self.generate_quiz)
        
        workflow.add_edge(START, "retrieve_docs")
        workflow.add_edge("retrieve_docs", "generate_quiz")
        workflow.add_edge("generate_quiz", END)

        main_graph = workflow.compile()
        return main_graph
    
    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------
    def retrieve_docs(self, state):
        topic = state["topic"]    
            
        documents = self.retriever.invoke(topic)
        documents = [doc.page_content for doc in documents]
              
        return {
            **state,
            "documents": documents
        }
    

    def generate_quiz(self, state):
        topic = state["topic"]
        documents = state["documents"]
        
        quiz = self.quiz_generator.invoke(
            {"topic": topic, "documents": documents}
        )
        return {
            **state,
            "quiz": quiz
        }
       
    # --------------------------------------------------
    # Interface
    # --------------------------------------------------
    def get_response(self, topic, streaming=False):
        if streaming:
            return self.main_graph.stream({"topic": topic})
        else: 
            return self.main_graph.invoke({"topic": topic})
    
    
# ----------------------------------------------------------------------
# State
# ----------------------------------------------------------------------
class GraphState(TypedDict):
    topic: str
    documents: List[str]
    quiz: str