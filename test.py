from utils.db import client

print("MongoDB Connected Successfully")

print(client.list_database_names())