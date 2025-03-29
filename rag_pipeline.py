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
import re
import weakref
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Prevents CUDA usage
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Disables TensorFlow optimizations

class ArtistIDOutputParser(BaseOutputParser[List[str]]):
    def parse(self, text: str) -> List[str]:
        # print("🔍 Raw LLM Response:", text)  # Debugging print statement

        # Allow single ID or comma-separated multiple IDs
        pattern = r'67[a-z0-9]{22}'  # Pattern for MongoDB ObjectIDs
        ids = re.findall(pattern, text)
        
        # Remove duplicates while preserving order
        unique_ids = []
        for id in ids:
            if id not in unique_ids:
                unique_ids.append(id)

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
            model_name="sentence-transformers/all-MiniLM-L6-v2",  # Smaller, ~100MB RAM
            model_kwargs={"device": "cpu"}
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=300,
            timeout=None,
            max_retries=2,
        )
        self.vector_db = None
        self.output_parser = ArtistIDOutputParser()
        
        # Update your prompt in the __init__ method
        self.prompt = ChatPromptTemplate.from_template("""
            System: You are a matching system that MUST output a minimum of 2 matching artist IDs and has no maximum limit.
            If exactly matching artists aren't found, relax the criteria to find the closest matches.
            Never return fewer than 2 artist IDs unless the available artists list is completely empty.

            Human: Match artists with these requirements:
            Client Requirements: {input}
            Available Artists: {context}

            Matching priority:
            1. First try with exact matches on all criteria:
            - Experience level exact match
            - Score exact match
            - Skills and Work title alignment
            
            2. If fewer than 2 matches are found, relax criteria in this order:
            - Allow partial skills/title matches
            - Allow similar (not exact) experience levels
            - Allow scores within a reasonable range
            
            3. IMPORTANT: Always return at least 2 artist IDs unless there are zero artists available.

            **Output the artist IDs, separated by commas. You MUST return at least 2 IDs.**

            Example Output:
            67a1234567890abcdef1234,67a234567890abcdef12345,67a3456789abcdef123456

            Assistant:
        """)

    def create_vectorstore(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        self.docs = text_splitter.split_documents(self.docs)
        
        # Filter out documents with empty embeddings
        valid_docs = []
        for doc in self.docs:
            embedding = self.embeddings.embed_query(doc.page_content)
            if embedding:
                valid_docs.append(doc)
            else:
                print(f"⚠️ Skipping document due to empty embedding: {doc.page_content}")
        
        if not valid_docs:
            raise ValueError("No valid documents with embeddings found. Check document content or embedding model.")
        
        self.vector_db = Chroma.from_documents(
            valid_docs, 
            self.embeddings,
            persist_directory="./chroma_db"  # Store vectors persistently to reduce RAM usage
        )

    def createDocRetrievalChain(self):
        document_chain = create_stuff_documents_chain(
            self.llm, 
            self.prompt,
            output_parser=self.output_parser
        )
        retriever = self.vector_db.as_retriever()

        # 🔍 Print retrieved documents before passing to LLM
        retrieved_docs = retriever.get_relevant_documents(self.client_doc)
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