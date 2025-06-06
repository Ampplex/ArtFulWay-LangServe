from typing import List
from connection import db
from langchain.schema import Document
from bson import ObjectId

class GetDocuments:
    def __init__(self, client_id: str):
        """Initialize with MongoDB collections and client_id."""
        self.artist = db['artist']
        self.projects = db['projects']
        self.client_id = client_id  # Store the client ID correctly

    def get_available_artists(self) -> List[Document]:
        """Fetches available artists from MongoDB and returns them as structured documents."""
        # Use MongoDB aggregation to get distinct artists
        pipeline = [
            {"$match": {"isAvailable": True}},
            {"$group": {"_id": "$_id", "doc": {"$first": "$$ROOT"}}}
        ]
        available_users = list(self.artist.aggregate(pipeline))
        
        print(f"Found {len(available_users)} available unique artists in database")
        
        # Convert MongoDB data into structured documents
        documents = [
            Document(
                page_content=f"""Artist Name: {user['doc'].get('artist_name', 'N/A')}
                Work Title: {user['doc'].get('work_title', 'N/A')}
                Experience: {user['doc'].get('experience', 'N/A')}
                Description: {user['doc'].get('description', 'N/A')}
                Score: {user['doc'].get('score', 'N/A')}
                Artist ID: {str(user['_id'])}""",
                metadata={
                    "artist_id": str(user['_id']),  # Add artist_id to metadata
                    "isAvailable": user['doc'].get("isAvailable", False),
                    "work_title": user['doc'].get("work_title", "N/A"),
                    "experience": user['doc'].get("experience", "N/A"),
                    "score": user['doc'].get("score", "N/A")
                }
            )
            for user in available_users
        ]
        
        return documents
    
    def get_clientInfo(self, project_id: str) -> List[Document]:
        """Fetches client project details from MongoDB and returns them as structured documents."""
        client_documents = []

        try:
            client_obj_id = ObjectId(self.client_id)  # Convert client_id to ObjectId
        except Exception as e:
            print(f"Invalid client_id: {self.client_id} - {e}")
            return []

        project_data = self.projects.find_one({"client_id": client_obj_id, "_id": ObjectId(project_id)})  # Find project using dynamic client_id

        if project_data:
            document = Document(
                page_content=f"""Project Title: {project_data.get('project_title', 'N/A')}
                Description: {project_data.get('description', 'N/A')}
                Budget: {project_data.get('project_budget', 'N/A')}
                Deadline: {project_data.get('deadline', 'N/A')}
                Experience Required: {project_data.get('experience_required', 'N/A')}
                Status: {project_data.get('project_status', 'N/A')}
                Score Required: {project_data.get('score_required', 'N/A')}""",
                metadata={
                    "client_id": str(project_data["_id"]),  # Convert ObjectId to string
                    "project_title": project_data.get("project_title", "N/A"),
                    "budget": project_data.get("budget", "N/A"),
                    "deadline": project_data.get("deadline", "N/A"),
                    "assigned_expert_id": str(project_data["assigned_expert_id"]) if project_data.get("assigned_expert_id") else None,
                    "experience_required": project_data.get("experience_required", "N/A"),
                    "status": project_data.get("status", "N/A"),
                    "requested_timeStamp": project_data.get("requested_timeStamp", "N/A"),
                    "score_required": project_data.get("score_required", "N/A")
                }
            )
            client_documents.append(document)

        # print("client documents: ", client_documents)
        return client_documents