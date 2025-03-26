from pymongo import MongoClient

# Replace with your connection string
MONGO_URI = "mongodb+srv://admin2:admin23@artfulwaycluster0.q52jt.mongodb.net/?retryWrites=true&w=majority&appName=ArtFulWayCluster0/Users"

client = MongoClient(MONGO_URI)
db = client["Users"]

print("Connected to MongoDB Atlas!")