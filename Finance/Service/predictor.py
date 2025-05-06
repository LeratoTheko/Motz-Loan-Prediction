# Service/predictor.py

import joblib
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from django.conf import settings

# Load models
loan_default_model_path = os.path.join(settings.BASE_DIR, 'Service', 'static', 'model', 'loan_approval_model.pkl')
loan_amount_model_path = os.path.join(settings.BASE_DIR, 'Service', 'static', 'model', 'loan_amount_optimization_model.pkl')

loan_default_model = joblib.load(loan_default_model_path)
loan_amount_model = joblib.load(loan_amount_model_path)

# Feature lists
LOAN_DEFAULT_FEATURES = [
    'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term',
    'Credit_History', 'Gender', 'Married', 'Education',
    'Self_Employed', 'Dependents', 'Property_Area'
]

LOAN_AMOUNT_FEATURES = [
    'ApplicantIncome', 'CoapplicantIncome', 'Loan_Amount_Term',
    'Credit_History', 'Dependents', 'Self_Employed',
    'Education', 'Property_Area', 'TotalIncome', 'IncomeToLoanTerm'
]

# Scalers
default_scaler = StandardScaler()
amount_scaler = StandardScaler()

# --- Preprocessors ---
def preprocess_loan_default(data: dict):
    """Preprocess input for loan default prediction."""
    X = np.array([[data[feat] for feat in LOAN_DEFAULT_FEATURES]])
    # Scale numeric features
    numeric_indices = [0, 1, 2, 3]
    X[:, numeric_indices] = default_scaler.fit_transform(X[:, numeric_indices])
    return X

def preprocess_loan_amount(data: dict):
    """Preprocess input for loan amount prediction."""
    X = np.array([[data[feat] for feat in LOAN_AMOUNT_FEATURES]])
    # Scale numeric features
    numeric_indices = [0, 1, 2, 8, 9]  # TotalIncome and IncomeToLoanTerm
    X[:, numeric_indices] = amount_scaler.fit_transform(X[:, numeric_indices])
    return X

# --- Prediction Functions ---
def predict_loan_approval(data: dict):
    X = preprocess_loan_default(data)
    prob = loan_default_model.predict_proba(X)[0][1]
    threshold = 0.2208
    prediction = int(prob >= threshold)
    return prediction, round(prob, 4)

def predict_loan_amount(data: dict):
    X = preprocess_loan_amount(data)
    predicted = loan_amount_model.predict(X)[0]
    return float(round(predicted, 2))
