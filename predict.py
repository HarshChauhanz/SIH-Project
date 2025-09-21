import joblib
import pandas as pd

# Load the trained model and all preprocessing objects
try:
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    le_target = joblib.load("le_target.pkl")
    label_encoders = joblib.load("label_encoders.pkl")
    features = joblib.load("features.pkl")
    print("Model and preprocessing objects loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading model files: {e}. Please run model.py first.")
    # Assign None to indicate failure, so the app doesn't crash completely
    model, scaler, le_target, label_encoders, features = [None] * 5

def predict_risk(data):
    """Predicts the risk level for a single student."""
    if not all([model, scaler, le_target, label_encoders, features]):
        return {"error": "Model not loaded. Check server logs."}

    try:
        df = pd.DataFrame([data])
        
        # Apply the saved label encoders to the categorical columns
        for col, le in label_encoders.items():
            if col in df.columns:
                # Handle unseen labels by assigning a default value (e.g., -1 or a specific code)
                df[col] = df[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)

        # Ensure all required feature columns are present and in the correct order
        df = df.reindex(columns=features, fill_value=0)

        # Scale the features
        scaled_features = scaler.transform(df)
        
        # Make prediction
        prediction_encoded = model.predict(scaled_features)
        
        # Decode the prediction back to the original label (e.g., "Low_Risk")
        risk_level = le_target.inverse_transform(prediction_encoded)

        return {"risk_level": risk_level[0]}
    except Exception as e:
        return {"error": f"Prediction error: {str(e)}"}

def batch_predict_risk(student_data_list):
    """Performs batch prediction on a list of student data."""
    return [predict_risk(student) for student in student_data_list]