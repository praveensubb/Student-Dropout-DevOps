import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from pathlib import Path

# Get project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load dataset
data = pd.read_csv(BASE_DIR / "dataset" / "students.csv")

# Features
X = data[
    [
        "attendance",
        "cgpa",
        "internal",
        "backlogs",
        "assignments",
        "behavior"
    ]
]

# Target
y = data["risk"]

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# Save model
joblib.dump(model, BASE_DIR / "model" / "dropout_model.pkl")

print("Model trained successfully!")