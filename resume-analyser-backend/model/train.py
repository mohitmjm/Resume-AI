"""
Train a TF-IDF + Logistic Regression classifier on the Kaggle Resume Dataset.

Dataset: UpdatedResumeDataSet.csv
Source:  https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset
Place the CSV in: resume-analyser-backend/data/UpdatedResumeDataSet.csv

Run:
    cd resume-analyser-backend
    python model/train.py

Output: model/classifier.pkl
"""
import os
import re
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "UpdatedResumeDataSet.csv")
MODEL_OUT = os.path.join(os.path.dirname(__file__), "classifier.pkl")


def clean_text(text: str) -> str:
    text = re.sub(r"http\S+|www\.\S+", " ", text)       # remove URLs
    text = re.sub(r"[^a-zA-Z\s#+.]", " ", text)          # keep letters, #, +, .
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def train():
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Dataset not found at: {DATA_PATH}")
        print("Download UpdatedResumeDataSet.csv from Kaggle and place it in the data/ folder.")
        sys.exit(1)

    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"  {len(df)} rows, categories: {df['Category'].nunique()}")

    df["clean"] = df["Resume"].astype(str).apply(clean_text)

    X = df["clean"].values
    y = df["Category"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Fitting TF-IDF vectoriser (max 6000 features)...")
    vectorizer = TfidfVectorizer(
        max_features=6000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training Logistic Regression classifier...")
    clf = LogisticRegression(
        max_iter=1000,
        C=5.0,
        solver="lbfgs",
        multi_class="multinomial",
        n_jobs=-1,
    )
    clf.fit(X_train_vec, y_train)

    y_pred = clf.predict(X_test_vec)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    model_data = {
        "vectorizer": vectorizer,
        "classifier": clf,
        "classes": clf.classes_.tolist(),
    }
    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    joblib.dump(model_data, MODEL_OUT)
    print(f"\n✓ Model saved to {MODEL_OUT}")


if __name__ == "__main__":
    train()
