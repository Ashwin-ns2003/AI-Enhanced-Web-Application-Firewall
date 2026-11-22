"""Train the Random Forest on data/payloads.csv and save it as model.pkl"""
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from features import extract_features

df = pd.read_csv("data/payloads.csv")
print("Total samples:", len(df))
print(df["label"].value_counts().rename({0: "normal", 1: "attack"}), "\n")

# 1. Turn each text into numbers
X = [extract_features(t) for t in df["text"]]
y = df["label"]

# 2. Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

# 3. Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 4. Evaluate
pred = model.predict(X_test)
print("Accuracy:", round(accuracy_score(y_test, pred), 3))
print(classification_report(y_test, pred, target_names=["normal", "attack"]))

# 5. Save
joblib.dump(model, "model.pkl")
print("Saved model.pkl")
