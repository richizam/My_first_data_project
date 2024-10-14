#salary_predictor.py

import joblib
import pandas as pd
import numpy as np
import os

class SalaryPredictor:
    def __init__(self, model_path='stacking_model.pkl'):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model = joblib.load(model_path)

    def predict(self, data):
        try:
            df = pd.DataFrame([data])
            prediction = self.model.predict(df)
            rounded_prediction = np.round(prediction[0] / 100) * 100
            return float(rounded_prediction)
        except Exception as e:
            print(f"Error in salary prediction: {e}")
            return 0.0  # Return a default value if prediction fails

# Initialize the predictor
try:
    salary_predictor = SalaryPredictor()
except Exception as e:
    print(f"Error initializing SalaryPredictor: {e}")
    salary_predictor = None