import pandas as pd

def load_finance(path='../data/processed/finance_clean.csv'):
    df = pd.read_csv(path, parse_dates=['date_time'])
    return df

def load_anomaly(path='../data/processed/anomaly_results.csv'):
    df = pd.read_csv(path)
    return df