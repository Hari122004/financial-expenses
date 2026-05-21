# 💰 Financial Expense Tracking & Analytics System

An AI-powered financial management application developed using Python and Streamlit to help users track expenses, analyze spending behavior, and predict future expenses using Machine Learning.

---

# 📌 Project Objective

Build a smart financial management system to:

✅ Track expenses  
✅ Categorize spending  
✅ Analyze monthly budgets  
✅ Predict future expenses  

---

# 🚀 Features

## 💵 Expense Tracking
- Add daily expenses
- Store expense records
- Dynamic expense updates
- Expense history management

## 📊 Financial Analytics
- Spending analysis
- Monthly budget tracking
- Remaining balance calculation
- Spending patterns visualization

## 📈 Interactive Charts
- Pie Charts
- Bar Charts
- Expense analytics dashboard
- Real-time visualization updates

## 🤖 AI Expense Prediction
- Predict future expenses
- Analyze spending trends
- Machine Learning integration
- Budget forecasting

## 🔐 Authentication System
- User Signup/Login
- Password hashing using bcrypt
- Session management
- JWT support

## 📧 Email Notification System
- SMTP Gmail integration
- Login alerts
- Budget warning emails
- Financial summary reports

---

# 🧠 Technologies Used

## Frontend
- Streamlit

## Backend
- Python

## Database
- SQLite

## Authentication
- bcrypt
- JWT

## Machine Learning
- Scikit-learn

## Visualization
- Plotly
- Pandas

## Email Service
- SMTP Gmail

## Environment Management
- python-dotenv

---

# 📂 Project Structure

```bash
expense-tracker/
│
├── database/
│   └── expense.db
│
├── models/
│   └── expense_predictor.pkl
│
├── pages/
│   ├── add_expense.py
│   ├── analytics.py
│   ├── Dashboard.py
│   └── prediction.py
│
├── utils/
│   ├── auth.py
│   ├── charts.py
│   ├── db.py
│   ├── jwt_handler.py
│   └── mail.py
│
├── .env
├── .gitignore
├── app.py
├── ml_model.py
├── requirements.txt
└── README.md
