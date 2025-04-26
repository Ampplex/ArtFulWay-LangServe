from typing import List
from langchain.schema import BaseOutputParser
from getDocuments import GetDocuments
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma, FAISS
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import weakref
import os
from connection import db

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Prevents CUDA usage
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Disables TensorFlow optimizations

class ArtistIDOutputParser(BaseOutputParser[List[str]]):
    def parse(self, text: str) -> List[str]:
        print("\n🔍 Raw LLM Response:", text)  # Debugging print statement

        # Allow single ID or comma-separated multiple IDs
        pattern = r'67[a-z0-9]{22}'  # Pattern for MongoDB ObjectIDs
        ids = re.findall(pattern, text)
        
        # Remove duplicates while preserving order
        unique_ids = []
        for id in ids:
            if id not in unique_ids:
                unique_ids.append(id)

        print(f"📝 Found {len(unique_ids)} unique artist IDs")
        print(f"🎨 Artist IDs: {unique_ids}")

        if not unique_ids:
            print("⚠️ No artist IDs found in LLM response!")
        
        return unique_ids  # Return unique IDs only

class RAG_Pipeline:
    _instances = weakref.WeakSet()
    
    def __init__(self, clientId, project_id):
        self.__class__._instances.add(self)
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.client_id = clientId
        self.project_id = project_id
        
        self.docs = GetDocuments(self.client_id).get_available_artists()
        client_info = GetDocuments(self.client_id).get_clientInfo(project_id)
        
        if isinstance(client_info, list):
            self.client_doc = " ".join(str(item) for item in client_info)
        else:
            self.client_doc = str(client_info)
            
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,  # Slightly increase temperature from 0
            max_tokens=500,
            timeout=None,
            max_retries=2,
        )

        self.vector_db = None
        self.output_parser = ArtistIDOutputParser()
        
        self.prompt = ChatPromptTemplate.from_template("""
            System: You are a matching system that MUST return ALL suitable employeees.
            Your task is to identify EVERY employees that could potentially work on this project.
            It is CRITICAL that you do not exclude any potentially suitable employee.
            
            Human: Match artists with these requirements:
            Client Requirements: {input}
            Available employees: {context}
            
            Review all the employees and if matches with the client requirements and partially skills then return its details
            in the format:
            **Format: Only artist_id separated by commas**
        """)

    def create_vectorstore(self):
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=200
            )
            self.docs = text_splitter.split_documents(self.docs)
            self.vector_db = FAISS.from_documents(self.docs, self.embeddings)

    def createDocRetrievalChain(self):
        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        retriever = self.vector_db.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        return retrieval_chain

    def get_response(self):
        self.create_vectorstore()
        retrieval_chain = self.createDocRetrievalChain()
        response = retrieval_chain.invoke({"input": self.client_doc})
        return response['answer']