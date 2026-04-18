"""
Job Role Predictor.

Two modes:
  1. ML mode  — TF-IDF + Logistic Regression trained on Kaggle UpdatedResumeDataSet.csv
  2. Fallback — rule-based keyword matching (works without the dataset)

The model is trained once via `model/train.py` and saved to `model/classifier.pkl`.
If the pkl doesn't exist, fallback mode is used automatically.
"""
import os
import re
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "classifier.pkl")

# ---------------------------------------------------------------------------
# Rule-based fallback (always available, no training needed)
# ---------------------------------------------------------------------------
ROLE_KEYWORDS = {
    "Data Scientist": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
        "pandas", "numpy", "statistics", "python", "data science", "nlp", "computer vision",
        "xgboost", "neural network", "model training", "feature engineering",
    ],
    "Python Developer": [
        "python", "django", "flask", "fastapi", "sqlalchemy", "celery",
        "pytest", "rest api", "backend", "web development",
    ],
    "Web Designer": [
        "html", "css", "figma", "adobe xd", "ui", "ux", "responsive design",
        "javascript", "bootstrap", "sass", "photoshop", "illustrator",
    ],
    "Java Developer": [
        "java", "spring", "spring boot", "hibernate", "maven", "gradle",
        "microservices", "jvm", "junit", "restful",
    ],
    "Frontend Developer": [
        "react", "angular", "vue", "javascript", "typescript", "html", "css",
        "redux", "webpack", "jest", "responsive",
    ],
    "DevOps Engineer": [
        "docker", "kubernetes", "jenkins", "ci/cd", "terraform", "ansible",
        "aws", "gcp", "azure", "linux", "bash", "monitoring", "helm",
    ],
    "Network Security Engineer": [
        "cybersecurity", "firewall", "network", "penetration testing", "owasp",
        "encryption", "vpn", "cisco", "ethical hacking", "vulnerability",
    ],
    "Business Analyst": [
        "business analysis", "requirements", "stakeholder", "agile", "scrum",
        "jira", "excel", "power bi", "tableau", "process improvement", "sql",
    ],
    "Database Administrator": [
        "sql", "postgresql", "mysql", "oracle", "mongodb", "database design",
        "query optimisation", "stored procedures", "backup", "replication",
    ],
    "Android Developer": [
        "android", "kotlin", "java", "android studio", "mobile", "xml",
        "firebase", "rest api", "gradle",
    ],
    "iOS Developer": [
        "swift", "objective-c", "xcode", "ios", "cocoa touch", "uikit",
        "swiftui", "core data", "app store",
    ],
    "Testing Engineer": [
        "testing", "selenium", "pytest", "junit", "test automation",
        "qa", "manual testing", "api testing", "postman", "cypress",
    ],
    "Mechanical Engineer": [
        "autocad", "solidworks", "catia", "ansys", "manufacturing",
        "mechanical design", "thermodynamics", "fluid mechanics", "cam", "cnc",
    ],
    "HR": [
        "recruitment", "talent acquisition", "onboarding", "payroll", "hrms",
        "employee relations", "performance management", "training", "hr policies",
    ],
    "Operations Manager": [
        "operations", "supply chain", "logistics", "process improvement",
        "kpi", "lean", "six sigma", "project management", "team management",
    ],
    "Blockchain Developer": [
        "blockchain", "ethereum", "solidity", "smart contracts", "web3",
        "nft", "defi", "cryptography", "truffle", "hardhat",
    ],
    "Data Engineer": [
        "spark", "hadoop", "kafka", "airflow", "etl", "data pipeline",
        "data warehouse", "bigquery", "snowflake", "hive", "data lake",
    ],
    "Cloud Architect": [
        "aws", "azure", "gcp", "cloud architecture", "serverless", "s3",
        "lambda", "ec2", "cloud formation", "terraform", "microservices",
    ],
}


def predict_job_roles(text: str, top_n: int = 5) -> list:
    """
    Returns a list of dicts:
      [{ "role": "Data Scientist", "confidence": 87, "source": "ml" | "rules" }, ...]
    """
    # Try ML model first
    if os.path.exists(MODEL_PATH):
        return _predict_ml(text, top_n)
    return _predict_rules(text, top_n)


def _predict_ml(text: str, top_n: int) -> list:
    """Use trained TF-IDF + LogReg model."""
    try:
        model_data = joblib.load(MODEL_PATH)
        vectorizer = model_data["vectorizer"]
        classifier = model_data["classifier"]
        classes = model_data["classes"]

        vec = vectorizer.transform([text])
        proba = classifier.predict_proba(vec)[0]

        top_indices = proba.argsort()[::-1][:top_n]
        return [
            {
                "role": classes[i],
                "confidence": round(float(proba[i]) * 100, 1),
                "source": "ml",
            }
            for i in top_indices
            if proba[i] > 0.01
        ]
    except Exception as e:
        print(f"[job_predictor] ML model failed ({e}), falling back to rules.")
        return _predict_rules(text, top_n)


def _predict_rules(text: str, top_n: int) -> list:
    """Pure keyword-based scoring."""
    lower = text.lower()
    scores = {}

    for role, keywords in ROLE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lower))
        if hits > 0:
            # Score = hit rate * 100, capped at 95
            scores[role] = min(95, round((hits / len(keywords)) * 100 * 2.5))

    sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {"role": r, "confidence": c, "source": "rules"}
        for r, c in sorted_roles[:top_n]
        if c > 0
    ] or [{"role": "General Professional", "confidence": 50, "source": "rules"}]
