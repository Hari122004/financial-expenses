import os
import certifi

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

# Load environment variables explicitly
load_dotenv()

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "expense_tracker")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI environment variable is required for MongoDB Atlas connection"
    )

allow_invalid_certs = os.getenv(
    "MONGODB_TLS_ALLOW_INVALID_CERTS",
    "False"
).lower() in ("true", "1", "yes", "y")

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=allow_invalid_certs
)

DB_AVAILABLE = True
try:
    client.admin.command("ping")
except (ServerSelectionTimeoutError, PyMongoError) as exc:
    DB_AVAILABLE = False
    print(
        "Warning: Could not connect to MongoDB Atlas during startup.",
        exc
    )

if not DB_AVAILABLE:
    print(
        "Warning: MongoDB Atlas connection unavailable. "
        "Login and signup will still render, but database operations may fail."
    )

db = client[MONGODB_DB]

users_collection = db["users"]
expenses_collection = db["expenses"]
oauth_states_collection = db["oauth_states"]

# -----------------------------------
# INDEXES
# -----------------------------------
try:
    users_collection.create_index("email", unique=True)
    expenses_collection.create_index([("user_id", 1), ("date", -1)])
    oauth_states_collection.create_index("created_at", expireAfterSeconds=300)
except PyMongoError:
    pass

from utils.auth import (                                                

hash_password,                                                      

verify_password)