from database.mongodb import get_db

db = get_db()
count = db.workflows.count_documents({})
print(f"Total Workflows in DB: {count}")
print("Sample:", list(db.workflows.find().limit(1)))
