from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    job_description = request.form["job_description"]
    cv_text = request.form["cv_text"]

    prompt = f"""
You are a professional CV analyzer. Analyze the CV against the job description below.

Job Description:
{job_description}

CV:
{cv_text}

Respond in exactly this format:
SCORE: [number out of 10]
MATCHED SKILLS: [comma separated list]
MISSING SKILLS: [comma separated list]
SUGGESTIONS:
1. [first suggestion]
2. [second suggestion]
3. [third suggestion]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content

    lines = result.strip().split("\n")
    score = ""
    matched = ""
    missing = ""
    suggestions = []

    for i, line in enumerate(lines):
        if line.startswith("SCORE:"):
            score = line.replace("SCORE:", "").strip()
        elif line.startswith("MATCHED SKILLS:"):
            matched = line.replace("MATCHED SKILLS:", "").strip()
        elif line.startswith("MISSING SKILLS:"):
            missing = line.replace("MISSING SKILLS:", "").strip()
        elif line.startswith("SUGGESTIONS:"):
            for j in range(i + 1, len(lines)):
                suggestion_line = lines[j].strip()
                if suggestion_line:
                    cleaned = suggestion_line.lstrip("123. ").strip()
                    suggestions.append(cleaned)

    return render_template("result.html",
                           score=score,
                           matched=matched,
                           missing=missing,
                           suggestions=suggestions)

if __name__ == "__main__":
    app.run(debug=True)
