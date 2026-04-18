"""
Auto-generate a professional summary and extract key resume metadata.
Supports variable-length summaries (20–80 words) via max_words param.
"""
import re


def extract_name(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
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
    match = re.search(r"(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)", text, re.I)
    if match:
        return f"{match.group(1)}+ years"
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
    return list(dict.fromkeys(edu))


def generate_summary(
    name: str,
    top_role: str,
    skills: list,
    years_exp: str,
    education: list,
    ats_score: int,
    max_words: int = 40,
) -> str:
    """
    Generate a professional summary targeting approximately max_words words.

    Tiers:
      ≤ 25 words  → ultra-brief (name, role, top skill)
      26–35 words → brief (role + top 3 skills)
      36–50 words → standard (role + skills + experience)
      51–65 words → detailed (+ education + ATS note)
      66+ words   → full (all details + quantified context)
    """
    name_str = name or "This candidate"
    verb = "is" if name else "appears to be"

    has_exp = years_exp and years_exp != "N/A"
    exp_clause = f"with {years_exp} of experience " if has_exp else ""
    edu_clause = f"Holds a {education[0]}." if education else ""

    ats_note = (
        "The resume is well-structured and ATS-friendly."
        if ats_score >= 70
        else "There is room to improve ATS optimisation."
    )

    # Build skill lists of varying depth
    skills_3  = ", ".join(skills[:3])  if skills else "various technologies"
    skills_6  = ", ".join(skills[:6])  if skills else "various technologies"
    skills_9  = ", ".join(skills[:9])  if skills else "various technologies"

    if max_words <= 25:
        # Ultra-brief: ~20 words
        text = (
            f"{name_str} {verb} a {top_role} professional"
            f"{' ' + exp_clause.strip() if has_exp else ''}. "
            f"Key skill: {skills_3.split(',')[0].strip() if skills else 'not detected'}."
        )

    elif max_words <= 35:
        # Brief: ~30 words
        text = (
            f"{name_str} {verb} a {top_role} professional "
            f"{exp_clause}skilled in {skills_3}. "
            f"{edu_clause}"
        )

    elif max_words <= 50:
        # Standard: ~40 words
        text = (
            f"{name_str} {verb} a {top_role} professional "
            f"{exp_clause}with expertise in {skills_6}. "
            f"{edu_clause} {ats_note}"
        )

    elif max_words <= 65:
        # Detailed: ~55 words
        text = (
            f"{name_str} {verb} an experienced {top_role} professional "
            f"{exp_clause}with strong expertise in {skills_6}. "
            f"{edu_clause} "
            f"Their technical profile spans multiple domains including "
            f"{skills_3}. {ats_note}"
        )

    else:
        # Full: ~70–80 words
        text = (
            f"{name_str} {verb} a highly skilled {top_role} professional "
            f"{exp_clause}with comprehensive expertise in {skills_9}. "
            f"{edu_clause} "
            f"Their profile demonstrates strong cross-functional technical knowledge "
            f"spanning software development, data management, and modern tooling. "
            f"With proficiency in {skills_3}, they are well-positioned for senior "
            f"roles in the field. {ats_note}"
        )

    # Trim to max_words as a hard cap
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words]).rstrip(",.;:") + "."

    return text.strip()
