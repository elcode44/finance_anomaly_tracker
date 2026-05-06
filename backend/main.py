from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Allow React frontend to talk to this API later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data once at startup
df_finance = pd.read_csv('../data/processed/finance_clean.csv', parse_dates=['date_time'])
df_anomaly = pd.read_csv('../data/processed/anomaly_results.csv')
df_anomalies = df_anomaly[df_anomaly['anomaly'] == -1].copy()

@app.get("/")
def root():
    return {"status": "Finance Tracker API running"}

@app.get("/summary")
def get_summary():
    # Spending by category
    by_category = (
        df_finance.groupby('category')['amount']
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={'amount': 'total'})
    )

    # Spending by month
    df_finance['month_str'] = df_finance['date_time'].dt.strftime('%Y-%m')
    by_month = (
        df_finance.groupby('month_str')['amount']
        .sum()
        .round(2)
        .reset_index()
        .rename(columns={'month_str': 'month', 'amount': 'total'})
        .sort_values('month')
    )

    return {
        "total_spent": round(df_finance['amount'].sum(), 2),
        "total_transactions": len(df_finance),
        "by_category": by_category.to_dict(orient='records'),
        "by_month": by_month.to_dict(orient='records'),
    }

@app.get("/transactions")
def get_transactions(page: int = 1, per_page: int = 20):
    start = (page - 1) * per_page
    end = start + per_page
    
    df_sorted = df_finance.sort_values('date_time', ascending=False)
    page_data = df_sorted.iloc[start:end].copy()
    page_data['date_time'] = page_data['date_time'].astype(str)

    return {
        "total": len(df_finance),
        "page": page,
        "per_page": per_page,
        "transactions": page_data.to_dict(orient='records')
    }

@app.get("/anomalies")
def get_anomalies():
    results = df_anomalies[[
        'TransactionAmount', 'AccountBalance', 
        'LoginAttempts', 'TransactionDuration',
        'hour', 'anomaly_score', 'reasons'
    ]].copy()
    
    results['TransactionDate'] = df_anomaly.loc[
        df_anomaly['anomaly'] == -1, 'TransactionDate'
    ].values
    
    results = results.sort_values('anomaly_score')
    
    return {
        "total_anomalies": len(results),
        "anomalies": results.head(50).to_dict(orient='records')
    }