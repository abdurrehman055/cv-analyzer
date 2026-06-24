import os
import pdfplumber
from flask import Flask, render_template, request, redirect, url_for, flash
from analyzer import analyze_cv
from database import init_db, save_analysis, get_all_analyses

app = Flask(__name__)
app.secret_key = os.urandom(24)

with app.app_context():
    init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    job_description = request.form.get("job_description", "").strip()
    cv_text = request.form.get("cv_text", "").strip()
    pdf_file = request.files.get("cv_pdf")

    # Extract text from PDF if uploaded
    if pdf_file and pdf_file.filename != "":
        try:
            with pdfplumber.open(pdf_file) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
                cv_text = "\n".join(pages).strip()
            if not cv_text:
                flash("The PDF appears to be empty or image-based. Please paste your CV text instead.", "danger")
                return redirect(url_for("index"))
        except Exception:
            flash("Could not read the PDF file. Please make sure it is a valid PDF or paste your CV text instead.", "danger")
            return redirect(url_for("index"))

    # Validate inputs
    if not cv_text:
        flash("Please upload a CV PDF or paste your CV text.", "danger")
        return redirect(url_for("index"))

    if not job_description:
        flash("Please paste a job description.", "danger")
        return redirect(url_for("index"))

    # Call OpenAI
    try:
        result = analyze_cv(cv_text, job_description)
    except Exception as e:
        flash(f"OpenAI API error: {str(e)}", "danger")
        return redirect(url_for("index"))

    # Save to database
    try:
        save_analysis(
            cv_text=cv_text,
            job_desc=job_description,
            score=result["score"],
            matched=result["matched"],
            missing=result["missing"],
            suggestions=result["suggestions"],
            summary=result["summary"],
        )
    except Exception:
        pass  # Don't block the user if saving fails

    return render_template("result.html", result=result)


@app.route("/history")
def history():
    analyses = get_all_analyses()
    return render_template("history.html", analyses=analyses)


if __name__ == "__main__":
    app.run(debug=True)
