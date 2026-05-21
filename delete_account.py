import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "expense_tracker")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
users_collection = db["users"]

# Delete the test account
email_to_delete = input("Enter email to delete: ")
result = users_collection.delete_one({"email": email_to_delete})

if result.deleted_count > 0:
    print(f"✓ Successfully deleted account: {email_to_delete}")
else:
    print(f"✗ No account found with email: {email_to_delete}")
