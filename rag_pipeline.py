from typing import List
from langchain.schema import BaseOutputParser
from getDocuments import GetDocuments
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import re
import weakref

class ArtistIDOutputParser(BaseOutputParser[List[str]]):
    def parse(self, text: str) -> List[str]:
        # print("🔍 Raw LLM Response:", text)  # Debugging print statement

        # Allow single ID or comma-separated multiple IDs
        pattern = r'67[a-z0-9]{22}'  # Pattern for MongoDB ObjectIDs
        ids = re.findall(pattern, text)

        if not ids:
            print("⚠️ No artist IDs found in LLM response!")

        return ids  # Return whatever is available

class RAG_Pipeline:
    _instances = weakref.WeakSet()
    
    def __init__(self, clientId):
        self.__class__._instances.add(self)
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.client_id = clientId
        
        self.docs = GetDocuments(self.client_id).get_available_artists()
        client_info = GetDocuments(self.client_id).get_clientInfo()
        
        if isinstance(client_info, list):
            self.client_doc = " ".join(str(item) for item in client_info)
        else:
            self.client_doc = str(client_info)
            
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={"device": "cpu"}  # Force CPU usage
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=300,
            timeout=None,
            max_retries=2,
        )
        self.vector_db = None
        self.output_parser = ArtistIDOutputParser()
        
        self.prompt = ChatPromptTemplate.from_template("""
            System: You are a matching system that ONLY outputs artist IDs. 
            If there are no matching artists, output an empty response. 

            Human: Match artists with these requirements:
            Client Requirements: {input}
            Available Artists: {context}

            Criteria:
            - Experience level exact match
            - Score exact match
            - Skills and Work title alignment

            **Output the available artist IDs, separated by commas. If no matching artists are found, return an empty response.**

            Example Output:
            67a1234567890abcdef1234,67a234567890abcdef12345
            or
            (empty response)

            Assistant:
        """)

    def create_vectorstore(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        self.docs = text_splitter.split_documents(self.docs) 
        self.vector_db = Chroma.from_documents(self.docs, self.embeddings)

    def createDocRetrievalChain(self):
        document_chain = create_stuff_documents_chain(
            self.llm, 
            self.prompt,
            output_parser=self.output_parser
        )
        retriever = self.vector_db.as_retriever()

        # 🔍 Print retrieved documents before passing to LLM
        # retrieved_docs = retriever.get_relevant_documents(self.client_doc)
        # print("🔍 Retrieved Documents for LLM:", retrieved_docs)

        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        return retrieval_chain

    def get_response(self) -> List[str]:
        self.create_vectorstore()
        retrieval_chain = self.createDocRetrievalChain()

        response = retrieval_chain.invoke({"input": self.client_doc})

        # Clean up vector DB to free memory
        del self.vector_db
        self.vector_db = None

        return response['answer']