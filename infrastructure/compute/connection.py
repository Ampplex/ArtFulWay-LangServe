from pymongo import MongoClient

# Replace with your connection string
MONGO_URI = "mongodb://localhost:27017/Users"

client = MongoClient(MONGO_URI)
db = client["Users"]

print("Connected to MongoDB Atlas!")