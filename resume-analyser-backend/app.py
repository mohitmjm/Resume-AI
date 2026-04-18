"""
Flask API — Smart Resume Analyser Backend
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from services.parser import parse_file
from services.skill_extractor import extract_skills
from services.ats_scorer import compute_ats_score
from services.job_predictor import predict_job_roles
from services.summariser import (
    extract_name, extract_contact,
    extract_years_experience, extract_education,
    extractive_summary,
)

app = Flask(__name__)
CORS(app)  # Allow all origins — restrict to your Netlify URL in production if needed

MAX_FILE_MB = 10


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model": _model_status()})


# ---------------------------------------------------------------------------
# Main analysis endpoint
# ---------------------------------------------------------------------------
@app.post("/api/analyse")
def analyse():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Send a PDF or DOCX as 'file'."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename."}), 400

    # File size check
    file.seek(0, 2)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > MAX_FILE_MB:
        return jsonify({"error": f"File too large ({size_mb:.1f} MB). Max {MAX_FILE_MB} MB."}), 413

    # 1. Parse
    try:
        text = parse_file(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Could not parse file: {e}"}), 500

    if len(text.strip()) < 50:
        return jsonify({
            "error": "Could not extract text. The file may be scanned or image-based. "
                     "Please use a text-based PDF or DOCX."
        }), 422

    # 2. Skills
    skills_data = extract_skills(text)
    all_skills = skills_data["all"]

    # 3. ATS score
    ats = compute_ats_score(text, all_skills)

    # 4. Job roles
    job_roles = predict_job_roles(text, top_n=5)

    # 5. Metadata + summary
    name = extract_name(text)
    contact = extract_contact(text)
    years_exp = extract_years_experience(text)
    education = extract_education(text)
    top_role = job_roles[0]["role"] if job_roles else "Professional"

    # summary_pct: % of resume text to include in summary (20–80), default 30
    try:
        summary_pct = int(request.form.get("summary_pct", 30))
        summary_pct = max(20, min(80, summary_pct))
    except (ValueError, TypeError):
        summary_pct = 30

    summary = extractive_summary(text, pct=summary_pct)

    return jsonify({
        "name": name,
        "contact": contact,
        "years_experience": years_exp,
        "education": education,
        "summary": summary,
        "ats": {
            "total": ats["total"],
            "grade": ats["grade"],
            "breakdown": ats["breakdown"],
        },
        "skills": skills_data,
        "job_roles": job_roles,
    })


def _model_status() -> str:
    model_path = os.path.join("model", "classifier.pkl")
    return "ml" if os.path.exists(model_path) else "rules (run model/train.py for ML mode)"


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
