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
        available_users = self.artist.find({"isAvailable": True})

        print("available artists: ", available_users)

        # Convert MongoDB data into structured documents
        documents = [
            Document(
                page_content=f"""Artist Name: {user.get('artist_name', 'N/A')}
                Work Title: {user.get('work_title', 'N/A')}
                Experience: {user.get('experience', 'N/A')}
                Description: {user.get('description', 'N/A')}
                Score: {user.get('score', 'N/A')}
                Artist ID: {str(user['_id'])}""",
                metadata={
                    "isAvailable": user.get("isAvailable", False),
                    "work_title": user.get("work_title", "N/A"),
                    "experience": user.get("experience", "N/A"),
                    "score": user.get("score", "N/A")
                }
            )
            for user in available_users
        ]
        print(documents)
        return documents
    
    def get_clientInfo(self) -> List[Document]:
        """Fetches client project details from MongoDB and returns them as structured documents."""
        client_documents = []

        try:
            client_obj_id = ObjectId(self.client_id)  # Convert client_id to ObjectId
        except Exception as e:
            print(f"Invalid client_id: {self.client_id} - {e}")
            return []

        project_data = self.projects.find_one({"client_id": client_obj_id, "_id": ObjectId("67d44c68216b280c5f7bb854")})  # Find project using dynamic client_id

        print("Client data: ", project_data)

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

        return client_documents