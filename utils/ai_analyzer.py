import os
import time
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


def test_connection():
    """Simple test to confirm Gemini API is working."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents="Say hello in one short sentence."
    )
    return response.text


def analyze_resume(resume_text, job_role=None, max_retries=3):
    """
    Sends resume text to Gemini and returns structured improvement suggestions.
    job_role: optional target job title/role to tailor feedback
    max_retries: number of times to retry if the model is temporarily overloaded
    """
    role_context = f" for a {job_role} position" if job_role else ""

    prompt = f"""
You are an expert resume reviewer and career coach.
Analyze the following resume{role_context} and provide clear, actionable feedback.

Structure your response in these sections using Markdown headings:

## Overall Impression
A brief 2-3 sentence summary of the resume's strengths and weaknesses.

## Strengths
Bullet points of what the resume does well.

## Areas to Improve
Bullet points of specific, actionable improvements (weak wording, missing metrics, formatting issues, etc.)

## Missing Elements
Bullet points of important sections or details that seem to be missing (e.g., quantifiable achievements, keywords, certifications).

## ATS Compatibility Notes
Brief notes on how well this resume would likely perform with Applicant Tracking Systems.

## Suggested Rewrites
Pick 2-3 weak bullet points from the resume and show a "Before" and "After" improved version.

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e)
            # Only retry on overload/unavailable errors
            if "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower():
                if attempt < max_retries - 1:
                    time.sleep(3)  # wait 3 seconds before retrying
                    continue
            # For other errors, fail immediately
            raise

    # If all retries failed
    raise last_error