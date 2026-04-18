"""
Auto-generate a professional summary and extract key resume metadata.
No external ML models — pure NLP heuristics.
"""
import re


def extract_name(text: str) -> str:
    """Heuristic: first non-empty line is usually the name."""
    for line in text.split("\n"):
        line = line.strip()
        # Name: 2-4 words, all capitalised, no digits
        if line and re.match(r"^[A-Z][a-zA-Z]+([\s][A-Z][a-zA-Z]+){1,3}$", line):
            return line
    return ""


def extract_contact(text: str) -> dict:
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    linkedin = re.search(r"linkedin\.com/in/[\w\-]+", text, re.I)
    github = re.search(r"github\.com/[\w\-]+", text, re.I)
    return {
        "email": email_match.group() if email_match else None,
        "phone": phone_match.group().strip() if phone_match else None,
        "linkedin": linkedin.group() if linkedin else None,
        "github": github.group() if github else None,
    }


def extract_years_experience(text: str) -> str:
    """Try to find a stated years of experience."""
    match = re.search(r"(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)", text, re.I)
    if match:
        return f"{match.group(1)}+ years"

    # Date range counting fallback
    ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)", text, re.I)
    if ranges:
        total = 0
        for start, end in ranges:
            try:
                s = int(start)
                e = 2024 if end.lower() in ("present", "current") else int(end)
                total += max(0, e - s)
            except ValueError:
                pass
        if total > 0:
            return f"~{total} years"
    return "N/A"


def extract_education(text: str) -> list:
    edu = []
    patterns = [
        r"(b\.?tech|b\.?e|bachelor[s]?|b\.?sc)\b[^\n]*",
        r"(m\.?tech|m\.?e|master[s]?|m\.?sc|mba|mca)\b[^\n]*",
        r"(ph\.?d\.?|doctorate)\b[^\n]*",
        r"(diploma|certificate|certification)\b[^\n]*",
    ]
    for p in patterns:
        matches = re.findall(p, text, re.I)
        for m in matches:
            s = m if isinstance(m, str) else " ".join(m)
            edu.append(s.strip()[:100])
    return list(dict.fromkeys(edu))  # deduplicate preserving order


def generate_summary(
    name: str,
    top_role: str,
    skills: list,
    years_exp: str,
    education: list,
    ats_score: int,
) -> str:
    """Build a one-paragraph professional summary."""
    skill_str = ", ".join(skills[:6]) if skills else "a variety of technologies"
    edu_str = education[0] if education else ""
    exp_str = f"with {years_exp} of experience " if years_exp != "N/A" else ""

    edu_clause = f" Holds a {edu_str}." if edu_str else ""
    ats_note = (
        "The resume is well-structured and ATS-friendly."
        if ats_score >= 70
        else "There is room to improve ATS optimisation."
    )

    return (
        f"{name + ' is' if name else 'This candidate appears to be'} a {top_role} professional "
        f"{exp_str}with expertise in {skill_str}.{edu_clause} "
        f"{ats_note}"
    )
