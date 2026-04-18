# Resume Analyser — Python Backend

## Setup

```bash
cd resume-analyser-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run

```bash
python app.py
# API available at http://localhost:5000
```

## Dataset (for ML mode)

1. Download `UpdatedResumeDataSet.csv` from Kaggle:
   https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset

2. Place it in `data/UpdatedResumeDataSet.csv`

3. Train the model:
   ```bash
   python model/train.py
   ```

Without the dataset, the app still works using keyword-based job role prediction.

## API

### POST /api/analyse
- Body: `multipart/form-data` with field `file` (PDF or DOCX)
- Response: JSON with `ats`, `skills`, `job_roles`, `summary`, `contact`, `education`

### GET /api/health
- Returns server status and whether ML model is loaded
