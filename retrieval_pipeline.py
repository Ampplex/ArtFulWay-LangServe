from langchain_astradb import AstraDBVectorStore
# Replace the problematic import with our custom implementation
from custom_embeddings import CustomHuggingFaceEmbeddings
import os
from dotenv import load_dotenv
import numpy as np
from getProjectDocument import get_project_document

load_dotenv()

class RetrievalPipeline:
    def __init__(self, project_id: str):
        self.client_project_doc = get_project_document(project_id=project_id)

        # Build query text (what the embedding will be based on)
        self.query_text = " ".join([
            self.client_project_doc.get("project_title", ""),
            self.client_project_doc.get("description", ""),
            self.client_project_doc.get("required_skills", ""),
            f"{self.client_project_doc.get('experience_required', '')} years experience",
            self.client_project_doc.get("score", "")
        ])

        # Set up embedding + Astra vector store using our custom embeddings
        self.embedding = CustomHuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vstore = AstraDBVectorStore(
            collection_name="artists_vector",
            embedding=self.embedding,
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        )

    def get_response(self):
        # Search top 6 similar artists
        results = self.vstore.similarity_search_with_score(self.query_text, k=6)

        scores = [score for _, score in results]
        mean_score = np.mean(scores)
        
        # print("Scores:", scores, "Mean score:", mean_score)

        # Filter by score threshold
        matched_artist_ids = [doc.metadata.get("mongo_id") for doc, score in results 
                             if score >= mean_score and score > 0.63]

        print("🎯 Matched Artist IDs:", matched_artist_ids)
        return matched_artist_ids