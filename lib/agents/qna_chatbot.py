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
from lib.prompts import QNA_PROMPT

   
# ----------------------------------------------------------------------
# Q&A Chatbot
# ----------------------------------------------------------------------
class QnAChatbot:
    def __init__(self, model=LONG_CONTEXT_LLM, system_prompt=QNA_PROMPT):
        self.model = model
        self.system_prompt = system_prompt
        
        self.retriever = self._create_retriever()
        self.answer_generator = self._create_answer_generator()
        
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
    
    
    def _create_answer_generator(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("user", "{question}"),
            ]
        )
        llm = ChatOpenAI(model=self.model)
        return prompt | llm | StrOutputParser()
        
    # --------------------------------------------------
    # Graph
    # --------------------------------------------------    
    def _create_main_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("retrieve_docs", self.retrieve_docs)
        workflow.add_node("generate_answer", self.generate_answer)
        
        workflow.add_edge(START, "retrieve_docs")
        workflow.add_edge("retrieve_docs", "generate_answer")
        workflow.add_edge("generate_answer", END)

        main_graph = workflow.compile()
        return main_graph
    
    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------
    def retrieve_docs(self, state):
        question = state["question"]    
            
        documents = self.retriever.invoke(question)
        documents = [doc.page_content for doc in documents]
              
        return {
            **state,
            "documents": documents
        }
    

    def generate_answer(self, state):
        quiz = state["quiz"]
        question = state["question"]
        documents = state["documents"]
        
        answer = self.answer_generator.invoke(
            {"quiz": quiz, "question": question, "documents": documents}
        )
        return {
            **state,
            "answer": answer
        }
       
    # --------------------------------------------------
    # Interface
    # --------------------------------------------------
    def get_response(self, quiz, question, streaming=False):
        if streaming:
            return self.main_graph.stream({"quiz": quiz, "question": question})
        else: 
            return self.main_graph.invoke({"quiz": quiz, "question": question})
    
    
# ----------------------------------------------------------------------
# State
# ----------------------------------------------------------------------
class GraphState(TypedDict):
    quiz: str
    question: str    
    documents: List[str]
    answer: str