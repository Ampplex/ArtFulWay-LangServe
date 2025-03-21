from infrastructure.compute.connection import db
from bson import ObjectId
from dotenv import load_dotenv
from rag_pipeline import RAG_Pipeline

load_dotenv(verbose=True)

class Allocator:
    def __init__(self, client_id):
        self.artist = db['artist']
        self.client = db['client']
        self.client_id = client_id
        self.rag_pipeline = RAG_Pipeline(clientId=self.client_id)  # Reuse instance

    def get_best_matches(self):
        print("🔍 Searching for best matches...")
        return self.rag_pipeline.get_response()