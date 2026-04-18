"""
Skill extraction using a curated taxonomy.
"""
import re

SKILL_TAXONOMY = {
    "Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
        "bash", "shell", "sql", "dart", "lua",
    ],
    "Frontend": [
        "react", "angular", "vue", "svelte", "next.js", "nuxt", "gatsby",
        "html", "css", "sass", "tailwind", "bootstrap", "redux", "webpack", "vite",
        "jquery", "three.js", "d3",
    ],
    "Backend": [
        "node.js", "express", "fastapi", "django", "flask", "spring boot", "laravel",
        "rails", "asp.net", "nestjs", "graphql", "rest api", "grpc", "microservices",
    ],
    "Databases": [
        "postgresql", "mysql", "mongodb", "redis", "sqlite", "elasticsearch",
        "cassandra", "dynamodb", "firebase", "oracle", "sql server", "neo4j",
    ],
    "Cloud & DevOps": [
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "github actions", "gitlab ci", "ci/cd", "nginx", "linux",
        "helm", "prometheus", "grafana",
    ],
    "ML & Data Science": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
        "matplotlib", "seaborn", "xgboost", "huggingface", "opencv",
        "data science", "statistics", "spacy", "nltk", "bert", "gpt", "llm",
    ],
    "Tools": [
        "git", "github", "jira", "confluence", "figma", "postman", "swagger",
        "linux", "agile", "scrum", "kanban",
    ],
    "Mobile": [
        "react native", "flutter", "android", "ios", "xamarin", "ionic",
    ],
    "Security": [
        "cybersecurity", "penetration testing", "owasp", "encryption", "oauth",
        "jwt", "ssl", "tls",
    ],
}

ALL_SKILLS = {skill: cat for cat, skills in SKILL_TAXONOMY.items() for skill in skills}
SORTED_SKILLS = sorted(ALL_SKILLS.keys(), key=len, reverse=True)


def extract_skills(text: str) -> dict:
    """
    Returns:
        {
          "all": ["python", "django", ...],
          "by_category": {"Languages": ["python"], "Backend": ["django"], ...}
        }
    """
    lower = text.lower()
    found = {}

    for skill in SORTED_SKILLS:
        pattern = r"(?<![a-z0-9\-])" + re.escape(skill) + r"(?![a-z0-9\-])"
        if re.search(pattern, lower):
            category = ALL_SKILLS[skill]
            found[skill] = category

    by_category = {}
    for skill, cat in found.items():
        by_category.setdefault(cat, []).append(skill)

    return {
        "all": list(found.keys()),
        "by_category": by_category,
    }
