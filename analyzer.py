import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_cv(cv_text, job_description):
    prompt = f"""
You are a professional CV analyzer. Analyze the CV against the job description and respond in EXACTLY this format with no extra text:

SCORE: [a number from 1 to 10]
SUMMARY: [one sentence overview of the candidate's fit]
MATCHED SKILLS: [comma separated list of skills the CV has that match the job]
MISSING SKILLS: [comma separated list of important skills from the job that are missing from the CV]
SUGGESTIONS:
1. [specific actionable improvement]
2. [specific actionable improvement]
3. [specific actionable improvement]

Job Description:
{job_description}

CV:
{cv_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    return parse_response(raw)


def parse_response(raw):
    result = {
        "score": "N/A",
        "summary": "",
        "matched": [],
        "missing": [],
        "suggestions": [],
    }

    lines = raw.split("\n")
    in_suggestions = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("SCORE:"):
            result["score"] = line.replace("SCORE:", "").strip()
            in_suggestions = False
        elif line.startswith("SUMMARY:"):
            result["summary"] = line.replace("SUMMARY:", "").strip()
            in_suggestions = False
        elif line.startswith("MATCHED SKILLS:"):
            raw_matched = line.replace("MATCHED SKILLS:", "").strip()
            result["matched"] = [s.strip() for s in raw_matched.split(",") if s.strip()]
            in_suggestions = False
        elif line.startswith("MISSING SKILLS:"):
            raw_missing = line.replace("MISSING SKILLS:", "").strip()
            result["missing"] = [s.strip() for s in raw_missing.split(",") if s.strip()]
            in_suggestions = False
        elif line.startswith("SUGGESTIONS:"):
            in_suggestions = True
        elif in_suggestions and line[0].isdigit():
            cleaned = line.lstrip("0123456789. ").strip()
            if cleaned:
                result["suggestions"].append(cleaned)

    return result
