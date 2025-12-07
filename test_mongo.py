from pymongo import MongoClient

uri = "mongodb+srv://vaibhavkaushal102_db_user:cluster0123_v@cluster0.3pxzzli.mongodb.net/?appName=Cluster0"
client = MongoClient(uri)
db = client["test_db"]

print("Collections:", db.list_collection_names())
print("Connection successful!")