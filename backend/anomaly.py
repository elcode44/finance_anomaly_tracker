from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def train_model(df):
    df_model = df.copy()
    le_type = LabelEncoder()
    le_channel = LabelEncoder()
    df_model['TransactionType_enc'] = le_type.fit_transform(df_model['TransactionType'])
    df_model['Channel_enc'] = le_channel.fit_transform(df_model['Channel'])

    features = [
        'TransactionAmount', 'TransactionDuration', 'LoginAttempts',
        'AccountBalance', 'hour', 'day_of_week', 'days_since_last',
        'TransactionType_enc', 'Channel_enc'
    ]

    model = IsolationForest(contamination=0.05, random_state=42)
    df_model['anomaly'] = model.fit_predict(df_model[features])
    df_model['anomaly_score'] = model.decision_function(df_model[features])
    return df_model

def explain_anomaly(row, df):
    reasons = []
    if row['LoginAttempts'] >= 3:
        reasons.append(f"High login attempts ({int(row['LoginAttempts'])})")
    if row['TransactionAmount'] > df['TransactionAmount'].quantile(0.95):
        reasons.append(f"Unusually large amount (${row['TransactionAmount']:.2f})")
    if row['TransactionAmount'] > row['AccountBalance'] * 0.5:
        reasons.append("Amount is over 50% of account balance")
    if row['hour'] < 6 or row['hour'] > 22:
        reasons.append(f"Transaction at unusual hour ({int(row['hour'])}:00)")
    if row['TransactionDuration'] > df['TransactionDuration'].quantile(0.95):
        reasons.append("Unusually long transaction duration")
    return reasons if reasons else ["Statistical outlier across multiple factors"]