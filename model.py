import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import joblib

# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_csv("output-2.csv")

# Drop ID-like columns
drop_cols = ["Student_ID", "AISHE_Code", "Institution_Code", 
             "Year", "Data_Source_Year", "Primary_Sources"]
df = df.drop(columns=drop_cols)

label_encoders = {}
for col in df.drop(columns=["Risk_Level"]).select_dtypes(include=["object"]).columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

le_target = LabelEncoder()
df["Risk_Level"] = le_target.fit_transform(df["Risk_Level"])

X = df.drop(columns=["Risk_Level"])
y = df["Risk_Level"]

smote = SMOTE(random_state=42, k_neighbors=1)
X_resampled, y_resampled = smote.fit_resample(X, y)

scaler = StandardScaler()
X_resampled_scaled = scaler.fit_transform(X_resampled)

X_train, X_test, y_train, y_test = train_test_split(
    X_resampled_scaled, y_resampled,
    test_size=0.2, random_state=42, stratify=y_resampled
)

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

joblib.dump(model, "model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(le_target, "le_target.pkl")
joblib.dump(list(X.columns), "features.pkl")