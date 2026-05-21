from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

# SAMPLE MODEL
model = LinearRegression()

X = np.array([[1], [2], [3], [4], [5]])

y = np.array([1000, 1500, 2000, 2500, 3000])

model.fit(X, y)

def predict_expense(day):

    prediction = model.predict([[day]])

    return round(prediction[0], 2)


def prepare_monthly_data(expenses):

    df = pd.DataFrame(expenses)

    if df.empty:
        return pd.DataFrame({
            "month_index": [],
            "year_month": [],
            "total_amount": []
        })

    df["expense_date"] = pd.to_datetime(df["expense_date"])
    df = df.sort_values("expense_date")
    df["year_month"] = df["expense_date"].dt.to_period("M").dt.to_timestamp("M")

    monthly = (
        df.groupby("year_month")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "total_amount"})
    )

    monthly["month_index"] = range(1, len(monthly) + 1)

    return monthly[["month_index", "year_month", "total_amount"]]


def train_and_predict(monthly_df, future_months=3):

    if monthly_df.empty:
        return {
            "avg_monthly": 0,
            "trend": "No Data",
            "confidence": "0%",
            "message": "Add expenses to enable prediction.",
            "predictions": pd.DataFrame({"month_label": [], "predicted_amount": []})
        }

    X = monthly_df[["month_index"]].values
    y = monthly_df["total_amount"].values

    model = LinearRegression()
    model.fit(X, y)

    future_indexes = np.arange(
        X.flatten()[-1] + 1,
        X.flatten()[-1] + 1 + future_months
    ).reshape(-1, 1)

    predictions = model.predict(future_indexes)
    predictions = np.maximum(predictions, 0)

    avg_monthly = round(float(np.mean(y)), 2)
    slope = float(model.coef_[0])
    trend = (
        "Increasing" if slope > 0
        else "Decreasing" if slope < 0
        else "Stable"
    )

    confidence = f"{round(model.score(X, y) * 100, 1)}%"

    last_month = monthly_df["year_month"].max()
    prediction_months = [
        (last_month + pd.DateOffset(months=i)).strftime("%b %Y")
        for i in range(1, future_months + 1)
    ]

    prediction_df = pd.DataFrame({
        "month_label": prediction_months,
        "predicted_amount": np.round(predictions, 2)
    })

    return {
        "avg_monthly": avg_monthly,
        "trend": trend,
        "confidence": confidence,
        "message": "Prediction based on your monthly expense history.",
        "predictions": prediction_df
    }


def detect_patterns(expenses):

    df = pd.DataFrame(expenses)

    if df.empty:
        return {"insights": ["No expense data available."]}

    insights = []
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    top_category = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(1)
    )

    if not top_category.empty:
        category = top_category.index[0]
        insights.append(
            f"Highest spend is in {category}. Review this category for savings."
        )

    average = df["amount"].mean()
    insights.append(
        f"Average expense amount is ₹{round(average, 2)}."
    )

    return {"insights": insights}


def predict_by_category(expenses):

    df = pd.DataFrame(expenses)

    if df.empty:
        return {}

    category_totals = df.groupby("category")["amount"].sum()
    return category_totals.round(2).to_dict()
