from connection import db
from bson import ObjectId
from dotenv import load_dotenv
from rag_pipeline import RAG_Pipeline

load_dotenv(verbose=True)

class Allocator:
    def __init__(self, client_id, project_id):
        self.artist = db['artist']
        self.client = db['client']
        self.client_id = client_id
        self.project_id = project_id
        self.rag_pipeline = RAG_Pipeline(clientId=self.client_id, project_id=self.project_id)  # Reuse instance

    def get_best_matches(self):
        print("🔍 Searching for best matches...")
        return self.rag_pipeline.get_response().split(",")  # Assuming the response is a comma-separated string of IDs