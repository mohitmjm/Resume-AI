"""
ATS (Applicant Tracking System) Score Calculator.

Scores the resume on 8 factors totalling 100 points.
Returns a breakdown dict so the frontend can chart each factor.
"""
import re


# ---------------------------------------------------------------------------
# Factor weights
# ---------------------------------------------------------------------------
FACTORS = {
    "Contact Info":        {"max": 10, "desc": "Email & phone present"},
    "Online Presence":     {"max": 5,  "desc": "LinkedIn / GitHub / portfolio URL"},
    "Skills Section":      {"max": 20, "desc": "Technical skills detected"},
    "Work Experience":     {"max": 20, "desc": "Work/experience section found"},
    "Education":           {"max": 15, "desc": "Education section found"},
    "Achievements":        {"max": 15, "desc": "Quantifiable results (numbers/%)"},
    "Resume Length":       {"max": 10, "desc": "Word count in optimal range"},
    "Formatting":          {"max": 5,  "desc": "Clean, parseable structure"},
}


def compute_ats_score(text: str, skills: list) -> dict:
    """
    Returns:
        {
          "total": 78,
          "breakdown": {
             "Contact Info": {"score": 8, "max": 10, "desc": "..."},
             ...
          }
        }
    """
    lower = text.lower()
    breakdown = {}

    # 1. Contact Info (10 pts)
    has_email = bool(re.search(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", lower))
    has_phone = bool(re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text))
    contact_score = (6 if has_email else 0) + (4 if has_phone else 0)
    breakdown["Contact Info"] = {
        "score": contact_score, "max": 10,
        "desc": FACTORS["Contact Info"]["desc"],
        "note": f"{'✓ Email' if has_email else '✗ Email'} · {'✓ Phone' if has_phone else '✗ Phone'}",
    }

    # 2. Online Presence (5 pts)
    has_url = bool(re.search(r"(linkedin|github|portfolio|behance|dribbble|stackoverflow)", lower))
    url_score = 5 if has_url else 0
    breakdown["Online Presence"] = {
        "score": url_score, "max": 5,
        "desc": FACTORS["Online Presence"]["desc"],
        "note": "✓ Found" if has_url else "✗ Add LinkedIn/GitHub",
    }

    # 3. Skills (20 pts) — based on count
    skill_count = len(skills)
    if skill_count >= 15:
        skill_score = 20
    elif skill_count >= 10:
        skill_score = 16
    elif skill_count >= 6:
        skill_score = 12
    elif skill_count >= 3:
        skill_score = 7
    else:
        skill_score = 2
    breakdown["Skills Section"] = {
        "score": skill_score, "max": 20,
        "desc": FACTORS["Skills Section"]["desc"],
        "note": f"{skill_count} skills detected",
    }

    # 4. Work Experience (20 pts)
    exp_keywords = ["experience", "employment", "work history", "professional",
                    "responsibilities", "projects", "internship", "worked at",
                    "developed", "implemented", "designed", "managed", "led"]
    exp_hits = sum(1 for kw in exp_keywords if kw in lower)
    exp_score = min(20, exp_hits * 3)
    breakdown["Work Experience"] = {
        "score": exp_score, "max": 20,
        "desc": FACTORS["Work Experience"]["desc"],
        "note": f"{exp_hits} experience indicators found",
    }

    # 5. Education (15 pts)
    edu_keywords = ["education", "university", "college", "bachelor", "master",
                    "phd", "degree", "b.e", "b.tech", "m.tech", "mca", "bca",
                    "b.sc", "m.sc", "graduation"]
    has_edu = any(kw in lower for kw in edu_keywords)
    edu_score = 15 if has_edu else 0
    breakdown["Education"] = {
        "score": edu_score, "max": 15,
        "desc": FACTORS["Education"]["desc"],
        "note": "✓ Found" if has_edu else "✗ Add education section",
    }

    # 6. Achievements / Quantifiables (15 pts)
    # Look for numbers, percentages, currency
    quant_matches = re.findall(r"\b\d+[\.,]?\d*\s*(%|percent|k|m|million|billion|users|customers|projects|years?|months?|times?|x\b)", lower)
    also_numbers = re.findall(r"increased|decreased|reduced|improved|grew|saved|achieved|delivered", lower)
    quant_count = len(quant_matches) + len(also_numbers)
    if quant_count >= 5:
        quant_score = 15
    elif quant_count >= 3:
        quant_score = 10
    elif quant_count >= 1:
        quant_score = 5
    else:
        quant_score = 0
    breakdown["Achievements"] = {
        "score": quant_score, "max": 15,
        "desc": FACTORS["Achievements"]["desc"],
        "note": f"{quant_count} quantifiable items detected",
    }

    # 7. Resume Length (10 pts)
    word_count = len(text.split())
    if 300 <= word_count <= 900:
        length_score = 10
    elif 200 <= word_count < 300 or 900 < word_count <= 1200:
        length_score = 7
    elif word_count < 200:
        length_score = 3
    else:
        length_score = 5
    breakdown["Resume Length"] = {
        "score": length_score, "max": 10,
        "desc": FACTORS["Resume Length"]["desc"],
        "note": f"{word_count} words (ideal: 300–900)",
    }

    # 8. Formatting (5 pts)
    # Presence of multiple lines and section-like headers
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    has_sections = len(lines) > 10
    format_score = 5 if has_sections else 2
    breakdown["Formatting"] = {
        "score": format_score, "max": 5,
        "desc": FACTORS["Formatting"]["desc"],
        "note": "✓ Structured" if has_sections else "✗ Add clear sections",
    }

    total = sum(f["score"] for f in breakdown.values())

    return {
        "total": total,
        "breakdown": breakdown,
        "grade": _grade(total),
    }


def _grade(score: int) -> str:
    if score >= 85: return "Excellent"
    if score >= 70: return "Good"
    if score >= 55: return "Average"
    if score >= 40: return "Below Average"
    return "Poor"
