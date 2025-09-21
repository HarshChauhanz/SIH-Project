import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import joblib

# Load the dataset
df = pd.read_csv("output-2.csv")

# --- Feature Engineering & Selection ---
# Drop columns that are IDs, codes, or metadata - they don't help in prediction.
useless_cols = [
    "Student_ID", "AISHE_Code", "Institution_Code", "Year", 
    "Data_Source_Year", "Primary_Sources", "State", "Academic_Year", "District"
]
df_cleaned = df.drop(columns=useless_cols)

# --- Preprocessing ---
# 1. Encode Categorical Features
label_encoders = {}
for column in df_cleaned.select_dtypes(include=['object']).columns:
    if column != 'Risk_Level':
        le = LabelEncoder()
        df_cleaned[column] = le.fit_transform(df_cleaned[column])
        label_encoders[column] = le

# 2. Encode Target Variable
le_target = LabelEncoder()
df_cleaned['Risk_Level'] = le_target.fit_transform(df_cleaned['Risk_Level'])

# --- Prepare Data for Modeling ---
X = df_cleaned.drop('Risk_Level', axis=1)
y = df_cleaned['Risk_Level']

# Handle class imbalance with SMOTE
smote = SMOTE(random_state=42, k_neighbors=1)
X_resampled, y_resampled = smote.fit_resample(X, y)

# --- Scaling and Splitting ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_resampled)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled
)

# --- Model Training ---
model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# --- Evaluation ---
y_pred = model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))

# --- Save all necessary files ---
print("Saving model and preprocessing objects...")
joblib.dump(model, "model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(le_target, "le_target.pkl")
joblib.dump(label_encoders, "label_encoders.pkl") # CRUCIAL: Save the fitted encoders
joblib.dump(list(X.columns), "features.pkl") # Save the final feature list
print("Files saved successfully.")