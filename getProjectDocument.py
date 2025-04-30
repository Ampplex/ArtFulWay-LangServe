from connection import db
from bson import ObjectId

def get_project_document(project_id: str) -> str:
    """
    Retrieves the project document from the database based on the given project ID.

    Args:
        project_id (str): The ID of the project to retrieve.

    Returns:
        str: The project document as a string.
    """
    projects = db['projects']
    try:
        project_data = projects.find_one({"_id": ObjectId(project_id)})

        response = {
            "project_title": project_data.get("project_title", "N/A"),
            "description": project_data.get("description", "N/A"),
            "required_skills": project_data.get("required_skills", "N/A"),
            "experience_required": project_data.get("experience_required", "N/A"),
            "score": project_data.get("score", "N/A"),
            "mongo_id": str(project_data["_id"])
        }

        if project_data:
            return response
        else:
            return "Project not found."
    except Exception as e:
        return f"Error retrieving project: {e}"