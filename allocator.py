from connection import db
from bson import ObjectId
from dotenv import load_dotenv
from rag_pipeline import RAG_Pipeline

load_dotenv(verbose=True)

class Allocator:
    def __init__(self, client_id):
        self.artist = db['artist']
        self.client = db['client']
        self.client_id = client_id  # Additional attribute to store client id for business service

    def get_best_matches(self):
        rp = RAG_Pipeline(clientId=self.client_id)
        # print(rp.get_response().split(', '))
        return rp.get_response()