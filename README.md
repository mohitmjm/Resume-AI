# ResumeAI — Smart Resume Analyser

An NLP-powered full-stack web application that analyses your resume and gives you:

- 🎯 **ATS Score** — 8-factor compatibility score (0–100)
- 💼 **Job Role Predictions** — ML model trained on Kaggle resume dataset
- 📊 **Skill Breakdown** — Radar chart across 9 tech categories
- 📝 **AI Summary** — Auto-generated professional summary

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React + Vite |
| Backend | Python + Flask |
| NLP | scikit-learn, PyMuPDF, python-docx |
| ML Dataset | Kaggle UpdatedResumeDataSet (25 job categories) |
| Charts | Recharts |

## Quick Start

### 1. Backend
```bash
cd resume-analyser-backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py                # runs on http://localhost:5000
```

### 2. Frontend
```bash
cd resume-analyser
npm install
npm run dev                  # runs on http://localhost:5175
```

### 3. Enable ML Mode (optional — needs Kaggle dataset)
1. Download `UpdatedResumeDataSet.csv` from [Kaggle](https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset)
2. Place in `resume-analyser-backend/data/`
3. Run: `python model/train.py`
4. Restart the Flask server

## Project Structure

```
Resume-AI/
├── resume-analyser/            # React frontend
│   └── src/
│       ├── pages/              # Home, Results, History
│       ├── components/         # Navbar, ScoreGauge
│       └── styles/
│
└── resume-analyser-backend/    # Python Flask backend
    ├── services/
    │   ├── parser.py           # PDF/DOCX text extraction
    │   ├── skill_extractor.py  # Taxonomy-based skill detection
    │   ├── ats_scorer.py       # 8-factor ATS scoring
    │   ├── job_predictor.py    # ML / rule-based role prediction
    │   └── summariser.py       # AI summary generation
    ├── model/
    │   └── train.py            # Kaggle dataset ML trainer
    └── app.py                  # Flask API
```

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Server + model status |
| `/api/analyse` | POST | Analyse resume (multipart/form-data, field: `file`) |
