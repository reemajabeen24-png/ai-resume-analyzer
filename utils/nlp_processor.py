import spacy
import re

# Load the spaCy English model once
nlp = spacy.load("en_core_web_sm")


def clean_text(text):
    """Basic cleanup: remove extra whitespace, weird symbols."""
    text = re.sub(r"\s+", " ", text)          # collapse multiple spaces/newlines
    text = re.sub(r"[^\w\s.,@+\-#/()]", "", text)  # remove weird symbols, keep useful ones
    return text.strip()


def get_word_count(text):
    return len(text.split())


def extract_entities(text):
    """
    Extract useful named entities: organizations, dates, etc.
    Returns a dictionary grouped by entity type.
    """
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)

    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))

    return entities


def basic_resume_stats(text):
    """Return a small dictionary of quick resume stats."""
    cleaned = clean_text(text)
    doc = nlp(cleaned)

    stats = {
        "word_count": get_word_count(cleaned),
        "sentence_count": len(list(doc.sents)),
        "has_email": bool(re.search(r"[\w.\-]+@[\w.\-]+\.\w+", text)),
        "has_phone": bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}", text)),
    }
    return stats


# A sample skill keyword bank — common tech/business skills to match against
SKILL_KEYWORDS = [
    "python", "java", "javascript", "sql", "html", "css", "react", "node.js",
    "machine learning", "deep learning", "nlp", "data analysis", "data science",
    "excel", "power bi", "tableau", "aws", "azure", "gcp", "docker", "kubernetes",
    "git", "github", "agile", "scrum", "project management", "communication",
    "leadership", "problem solving", "teamwork", "django", "flask", "streamlit",
    "pandas", "numpy", "tensorflow", "pytorch", "rest api", "c++", "c#",
    "linux", "devops", "ci/cd", "testing", "figma", "photoshop", "seo",
    "digital marketing", "content writing", "sales", "negotiation"
]


def extract_skills(text):
    """Match known skill keywords found in the resume text (case-insensitive)."""
    text_lower = text.lower()
    found_skills = []
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found_skills.append(skill)
    return sorted(set(found_skills))


def calculate_ats_score(text, stats):
    """
    A simple heuristic ATS-friendliness score out of 100.
    Not a real ATS engine — just a useful approximation for feedback.
    """
    score = 0
    reasons = []

    # Contact info
    if stats["has_email"]:
        score += 15
    else:
        reasons.append("Missing email address")

    if stats["has_phone"]:
        score += 15
    else:
        reasons.append("Missing phone number")

    # Length check (too short or too long resumes hurt ATS/readability)
    word_count = stats["word_count"]
    if 300 <= word_count <= 1000:
        score += 25
    elif word_count < 300:
        score += 10
        reasons.append("Resume seems too short — add more detail")
    else:
        score += 15
        reasons.append("Resume may be too long — consider trimming")

    # Skills found
    skills = extract_skills(text)
    skill_score = min(len(skills) * 3, 30)
    score += skill_score
    if len(skills) < 5:
        reasons.append("Few recognizable skill keywords found — consider adding more relevant skills")

    # Section keywords check
    section_keywords = ["experience", "education", "skills", "projects"]
    text_lower = text.lower()
    sections_found = [s for s in section_keywords if s in text_lower]
    score += len(sections_found) * 3.75  # up to 15 points

    if len(sections_found) < len(section_keywords):
        missing = set(section_keywords) - set(sections_found)
        reasons.append(f"Missing common sections: {', '.join(missing)}")

    score = round(min(score, 100))

    return {
        "score": score,
        "skills_found": skills,
        "reasons": reasons
    }