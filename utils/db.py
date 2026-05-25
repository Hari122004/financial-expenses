import os
import certifi

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

try:
    import streamlit as st
except Exception:
    st = None

# Load environment variables explicitly
load_dotenv()


def _get_config(name, default=None):
    value = os.getenv(name)
    if value:
        return value

    if st is not None:
        try:
            return st.secrets.get(name, default)
        except Exception:
            return default

    return default

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------
MONGODB_URI = _get_config("MONGODB_URI")
MONGODB_DB = _get_config("MONGODB_DB", "expense_tracker")

if not MONGODB_URI:
    DB_AVAILABLE = False
    client = None
    db = None
    users_collection = None
    expenses_collection = None
    oauth_states_collection = None
    print(
        "Warning: MONGODB_URI is not configured. Database features are disabled."
    )
else:
    allow_invalid_certs = _get_config(
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
if DB_AVAILABLE:
    try:
        users_collection.create_index("email", unique=True)
        expenses_collection.create_index([("user_id", 1), ("date", -1)])
        oauth_states_collection.create_index("created_at", expireAfterSeconds=300)
    except PyMongoError:
        pass

from utils.auth import (                                                

hash_password,                                                      

verify_password)