import pandas as pd
from bson.objectid import ObjectId

from utils.db import users_collection, expenses_collection


def add_expense(user_id, date, description, category, amount):
    """Add a new expense to the database."""
    try:
        expense_doc = {
            "user_id": user_id,
            "date": date,
            "description": description,
            "category": category,
            "amount": amount
        }
        expenses_collection.insert_one(expense_doc)
        return True, "Expense added successfully"
    except Exception as e:
        return False, str(e)


def get_user_id_by_username(username):
    """Get user ID by username."""
    try:
        user = users_collection.find_one({"username": username})
        return str(user["_id"]) if user else None
    except Exception as e:
        print(f"Error fetching user ID: {e}")
        return None


def get_user_expenses(user_id):
    """Retrieve all expenses for a user as a DataFrame."""
    try:
        docs = expenses_collection.find({"user_id": user_id}).sort("date", -1)
        rows = [
            (
                str(doc["_id"]),
                doc.get("date", ""),
                doc.get("description", ""),
                doc.get("category", ""),
                doc.get("amount", 0)
            )
            for doc in docs
        ]

        if not rows:
            return pd.DataFrame({
                "Date": [],
                "Description": [],
                "Category": [],
                "Amount": [],
                "expense_id": []
            })

        df = pd.DataFrame(rows, columns=["expense_id", "Date", "Description", "Category", "Amount"])
        return df[["Date", "Description", "Category", "Amount", "expense_id"]]
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        return pd.DataFrame({
            "Date": [],
            "Description": [],
            "Category": [],
            "Amount": [],
            "expense_id": []
        })


def delete_expense(expense_id):
    """Delete an expense by ID."""
    try:
        expenses_collection.delete_one({"_id": ObjectId(expense_id)})
        return True, "Expense deleted successfully"
    except Exception as e:
        return False, str(e)


def delete_all_user_expenses(user_id):
    """Delete all expenses for a user."""
    try:
        expenses_collection.delete_many({"user_id": user_id})
        return True, "All expenses deleted successfully"
    except Exception as e:
        return False, str(e)


def get_expense_summary(user_id):
    """Get expense summary for a user (total, by category, by month)."""
    try:
        docs = list(expenses_collection.find({"user_id": user_id}))

        category_summary = {}
        monthly_summary = {}

        for doc in docs:
            category = doc.get("category", "Other")
            amount = float(doc.get("amount", 0) or 0)
            category_summary[category] = category_summary.get(category, 0) + amount

            date_value = doc.get("date")
            if date_value:
                month = pd.to_datetime(date_value).strftime("%Y-%m")
            else:
                month = "Unknown"
            monthly_summary[month] = monthly_summary.get(month, 0) + amount

        sorted_monthly = {
            month: total
            for month, total in sorted(monthly_summary.items(), reverse=True)
        }

        return {
            "by_category": category_summary,
            "by_month": sorted_monthly
        }
    except Exception as e:
        print(f"Error getting summary: {e}")
        return {"by_category": {}, "by_month": {}}
