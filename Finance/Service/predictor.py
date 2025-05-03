# yourapp/predictor.py
import joblib
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from django.conf import settings

# Load model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(settings.BASE_DIR, 'Service', 'static', 'model', 'loan_approval_model.pkl')
model = joblib.load(model_path)

# Use the same order of features as training
FEATURE_COLUMNS = [
    'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term',
    'Credit_History', 'Gender', 'Married', 'Education',
    'Self_Employed', 'Dependents', 'Property_Area'
]

# Same scaler from training
scaler = StandardScaler()

def preprocess_input(data):
    """
    Accepts a dictionary and returns a feature vector
    Assumes all categorical values are already encoded
    """
    X = np.array([[data[feat] for feat in FEATURE_COLUMNS]])
    # Scale numeric columns
    numeric_indices = [0, 1, 2, 3]
    X[:, numeric_indices] = scaler.fit_transform(X[:, numeric_indices])
    return X

def predict_loan_approval(data):
    X = preprocess_input(data)
    prob = model.predict_proba(X)[0][1]
    threshold = 0.2208  # Optimal threshold from training
    prediction = int(prob >= threshold)
    return prediction, round(prob, 4)



