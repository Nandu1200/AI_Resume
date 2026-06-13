from flask import Flask, render_template, request
import pdfplumber
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        resume = request.files['resume']
        job_description = request.form.get("job_description", "")
        text = ""

        with pdfplumber.open(resume) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        text_lower = text.lower()

        # Resume Score (Realistic)
        score = 0

        # Contact Information
        if "@" in text:
            score += 5

        if "linkedin" in text_lower:
            score += 5

        if "github" in text_lower:
            score += 5

        # Education
        if "education" in text_lower:
            score += 15

        # Skills
        skills = [
            "python",
            "java",
            "c++",
            "sql",
            "react",
            "node",
            "mongodb",
            "machine learning",
            "flask",
            "javascript"
        ]

        skill_count = 0

        for skill in skills:
            if skill in text_lower:
                skill_count += 1

        score += min(skill_count * 2, 20)

        # Projects
        project_count = text_lower.count("project")
        score += min(project_count * 5, 20)

        # Experience
        if "experience" in text_lower:
            score += 10

        if "internship" in text_lower:
            score += 10

        # Certifications
        if "certificate" in text_lower:
            score += 5

        if "certification" in text_lower:
            score += 5

        # Resume Length
        if len(text) > 1000:
            score += 10

        if score > 100:
            score = 100

        # Strengths & Missing Skills
        strengths = []
        missing_skills = []

        if "python" in text_lower:
            strengths.append("Python")
        else:
            missing_skills.append("Python")

        if "sql" in text_lower:
            strengths.append("SQL")
        else:
            missing_skills.append("SQL")

        if "react" in text_lower:
            strengths.append("React")
        else:
            missing_skills.append("React")

        if "machine learning" in text_lower:
            strengths.append("Machine Learning")
        else:
            missing_skills.append("Machine Learning")

        if "project" in text_lower:
            strengths.append("Projects")
        else:
            missing_skills.append("Projects")

        # Recommended Jobs
        recommended_jobs = []

        if "python" in text_lower:
            recommended_jobs.append({
                "title": "Python Developer",
                "link": "https://www.naukri.com/python-developer-jobs"
            })

        if "sql" in text_lower:
            recommended_jobs.append({
                "title": "Data Analyst",
                "link": "https://www.naukri.com/data-analyst-jobs"
            })

        if "machine learning" in text_lower:
            recommended_jobs.append({
                "title": "Machine Learning Engineer",
                "link": "https://www.naukri.com/machine-learning-engineer-jobs"
            })

        if "react" in text_lower:
            recommended_jobs.append({
                "title": "Frontend Developer",
                "link": "https://www.naukri.com/react-js-developer-jobs"
            })

        if "flask" in text_lower:
            recommended_jobs.append({
                "title": "Backend Developer",
                "link": "https://www.naukri.com/backend-developer-jobs"
            })

        if len(recommended_jobs) == 0:
            recommended_jobs.append({
                "title": "Software Engineer",
                "link": "https://www.naukri.com/software-engineer-jobs"
            })

        # ATS Score
        ats_score = score

        if len(missing_skills) >= 3:
            ats_score -= 15

        if len(text) < 800:
            ats_score -= 10

        if "linkedin" not in text_lower:
            ats_score -= 5

        if "github" not in text_lower:
            ats_score -= 5

        if ats_score < 0:
            ats_score = 0

        # Resume vs Job Description Match
        match_score = 0
        matched_skills = []
        missing_jd_skills = []

        if job_description:
            jd_text = job_description.lower()

            jd_skills = [
                "python",
                "java",
                "sql",
                "react",
                "mongodb",
                "node",
                "machine learning",
                "flask",
                "javascript",
                "aws",
                "docker"
            ]

            total_skills = 0
            matched = 0

            for skill in jd_skills:
                if skill in jd_text:
                    total_skills += 1

                    if skill in text_lower:
                        matched += 1
                        matched_skills.append(skill)
                    else:
                        missing_jd_skills.append(skill)

            if total_skills > 0:
                match_score = int((matched / total_skills) * 100)

        # Grade
        if score >= 90:
            grade = "A+"
        elif score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"

        # Suggestions
        suggestions = []

        if "react" not in text_lower:
            suggestions.append("Learn React and add frontend projects.")

        if "sql" not in text_lower:
            suggestions.append("Add SQL skills to improve database knowledge.")

        if "machine learning" not in text_lower:
            suggestions.append("Add Machine Learning projects.")

        if "linkedin" not in text_lower:
            suggestions.append("Add your LinkedIn profile link.")

        if "github" not in text_lower:
            suggestions.append("Add your GitHub profile link.")

        if "internship" not in text_lower and "experience" not in text_lower:
            suggestions.append("Add internship or work experience if available.")

        # AI Summary using OpenRouter
        ai_summary = "AI Summary Not Available"

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
Analyze this resume and provide a professional summary in 5 lines.

Resume:
{text[:4000]}
"""
                    }
                ]
            )

            ai_summary = response.choices[0].message.content

        except Exception as e:
            ai_summary = f"AI Error: {str(e)}"

        # Interview Questions
        interview_questions = []

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
Based on this resume, generate 10 interview questions.

Resume:

{text[:4000]}

Return only questions.
"""
                    }
                ]
            )

            questions_text = response.choices[0].message.content
            interview_questions = questions_text.split("\n")

        except:
            interview_questions = [
                "Unable to generate interview questions."
            ]

        return render_template(
            'result.html',
            score=score,
            ats_score=ats_score,
            match_score=match_score,
            matched_skills=matched_skills,
            missing_jd_skills=missing_jd_skills,
            grade=grade,
            strengths=strengths,
            missing_skills=missing_skills,
            recommended_jobs=recommended_jobs,
            suggestions=suggestions,
            ai_summary=ai_summary,
            interview_questions=interview_questions,
            text=text[:3000]
        )

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)