from pymongo import MongoClient

# Replace with your connection string
MONGO_URI = "mongodb+srv://admin:admin087@artfulwaycluster0.q52jt.mongodb.net/Users"

client = MongoClient(MONGO_URI)
db = client["Users"]

print("Connected to MongoDB Atlas!")