🚀 AI Autonomous Hiring System

An end-to-end AI-powered technical hiring platform that automatically screens candidates using resumes, coding tests, and fraud detection — without manual interviews.

This system acts like a lightweight combination of:

ATS + Online Judge + Skill Evaluator

Built using Flask / FastAPI, Python execution sandbox, and automated scoring pipelines.

📌 Problem

Manual hiring is:

Slow

Biased

Non-scalable

Expensive

Recruiters waste time:

Reading resumes

Conducting basic interviews

Checking copied code

✅ Solution

This system automates:

Resume Upload
      ↓
AI Resume Scoring
      ↓
Random Coding Test
      ↓
Secure Code Compilation
      ↓
Auto Evaluation
      ↓
Fraud Detection
      ↓
Final Ranking

Only top candidates are shortlisted.

✨ Features
🧠 Resume Intelligence

PDF/DOC resume upload

Keyword extraction

Skill matching

ATS-style scoring

Experience weighting

💻 Coding Test Engine

Random question selection (100–500+ pool)

Live code editor

Multi-language support (Python/C++/Java)

Secure execution sandbox

Hidden test cases

Auto grading

⚡ Compiler / Judge

Code execution with:

time limit

memory limit

runtime capture

Compares outputs with expected results

Returns:

Passed / Failed

Execution time

Errors

🔐 Anti-Fraud Checks

Tab switching detection

Copy–paste detection

Randomized questions

Time tracking

Suspicious behavior flags

📊 Scoring System

Final score =

Resume Score (30%)
+ Coding Score (60%)
+ Integrity Score (10%)

Automatic ranking + shortlist.

🏗️ Architecture
Frontend (HTML/JS)
        ↓
Backend API (Flask/FastAPI)
        ↓
Modules:
   ├── resume_scoring.py
   ├── question_selector.py
   ├── compiler.py
   ├── judge.py
   ├── fraud_detector.py
   └── pipeline.py
        ↓
Results DB / JSON Storage
📂 Project Structure
ai-hiring-system/
│
├── app.py                 # Main server
├── project/
│   ├── question_selector.py
│   ├── judge.py
│   ├── resume_scoring.py
│   ├── compiler.py
│   ├── fraud_detector.py
│   └── pipeline.py
│
├── templates/
├── static/
├── resume/
├── questions/
├── testcases/
└── README.md
⚙️ Installation
1. Clone repo
git clone https://github.com/yourname/ai-hiring-system.git
cd ai-hiring-system
2. Create virtual env
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Run server
python app.py

Open:

http://localhost:5000
🧪 How It Works
Resume Scoring

NLP + keyword matching

Skill weights

Experience years

Coding Evaluation
compile → run → capture output → compare → score
Fraud Detection

Tracks:

tab changes

submission time anomalies

repeated outputs

suspicious patterns

📈 Example Flow

Candidate uploads resume

Gets auto score (e.g., 72/100)

Receives 5 random coding problems

Submits solutions

System evaluates automatically

Final score computed

Leaderboard updated

Top candidates shortlisted

🛠️ Tech Stack

Python

Flask / FastAPI

HTML + JS

Local execution sandbox

JSON/SQLite storage

🔒 Security Considerations

Sandboxed execution

Time limits

Memory limits

No direct OS access

Input/output isolation

⚠️ For production:
Use Docker or containerized sandbox.

🚀 Future Improvements

Webcam proctoring

AI plagiarism detection

LLM-based resume understanding

Cloud judge workers

Distributed scaling

Admin dashboard

Interview scheduling

🎯 Use Cases

Hackathons

Campus hiring

Startup screening

Online assessments

Bulk recruitment

📸 Demo
Resume → Test → Score → Rank → Hire
Fully automated.
🤝 Contributing

Pull requests welcome.

Steps:

fork → branch → commit → PR
