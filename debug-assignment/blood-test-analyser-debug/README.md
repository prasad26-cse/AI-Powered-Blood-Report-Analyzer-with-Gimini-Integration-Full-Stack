# 🩸 Blood Test Analyser (Gemini AI Powered)

A modern web application for uploading, analyzing, and interpreting blood test reports using Google Gemini AI and CrewAI agents. Built with FastAPI, React, Celery, and Redis.

---

## 🚀 Features
- **AI-Powered Analysis:** Uses Google Gemini AI for comprehensive blood test interpretation
- **PDF Upload:** Upload your blood test report in PDF format
- **Medical Agents:** Doctor, Verifier, Nutritionist, and Exercise Specialist agents provide multi-perspective analysis
- **User Authentication:** Secure registration and login
- **Dashboard:** View, download, and manage your reports
- **Celery & Redis:** Asynchronous, scalable background processing
- **Modern UI:** Built with React and Tailwind CSS

---

## 🛠️ Setup & Installation

### 1. **Clone the Repository**
```bash
git clone <repo-url>
cd debug-assignment/blood-test-analyser-debug
```

### 2. **Python Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **Frontend Setup**
```bash
cd frontend
npm install
cd ..
```

### 4. **Environment Variables**
- Copy `env.template` to `.env` and fill in your values (especially `GEMINI_API_KEY`).
- Get your Gemini API key from [Google MakerSuite](https://makersuite.google.com/app/apikey).

### 5. **Start Redis (Windows)**
```bash
Redis\redis-server.exe Redis\redis.windows.conf
```

### 6. **Start Backend (FastAPI + Celery)**
```bash
# In one terminal (API server):
python main.py

# In another terminal (Celery worker):
python start_celery_windows.py
```

### 7. **Start Frontend**
```bash
cd frontend
npm start
```

---

## 🧪 Usage
1. Register and log in on the web app.
2. Upload your blood test PDF.
3. Wait for AI-powered analysis to complete.
4. View, download, or share your report and recommendations.

---

## 🩺 How It Works
- **Upload:** PDF is securely stored and queued for analysis.
- **AI Analysis:** Gemini AI and CrewAI agents extract, interpret, and summarize results.
- **Results:** Receive a structured, human-readable report with medical, nutritional, and exercise advice.

---

## 🐞 Troubleshooting
- **No analysis result?**
  - Ensure your PDF is a real blood test report (not a scan/image-only file).
  - Check that your Gemini API key is valid and set in `.env`.
  - Make sure Redis and Celery are running.
- **Backend errors?**
  - Check logs in the terminal for FastAPI and Celery.
  - Restart the backend after changing environment variables.
- **Frontend issues?**
  - Run `npm install` in the `frontend` folder.
  - Make sure the backend is running on the expected port.

---

## 🤝 Contributing
Pull requests and issues are welcome! Please open an issue for bugs or feature requests.

---

## 📬 Contact & Help
- **Docs:** See `SETUP_API_KEY.md` for Gemini API setup
- **Email:** [Your Email Here]
- **GitHub Issues:** Use the Issues tab for support

---

**Made with ❤️ for modern medical AI applications.**

---

## 🐞 Critical Bugs & How They Were Fixed

### 1. Undefined LLM Assignment
**Bug:**
`llm = llm` is used without defining `llm`.

**How to Fix:**
Instantiate `llm` using a provider (e.g., OpenAI, HuggingFace) before assignment.
```python
from langchain.llms import OpenAI
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

---

### 2. Incorrect Agent Tool Parameter (`tool` vs `tools`)
**Bug:**
Used `tool=[...]` instead of `tools=[...]` in agent definitions.

**How to Fix:**
Replace all `tool=` with `tools=` in agent definitions.
```python
doctor = Agent(..., tools=[BloodTestReportTool().read_data_tool])
```

---

### 3. Async Method Used Incorrectly in Tools
**Bug:**
`read_data_tool` is async but not a `@staticmethod` or `@classmethod`. Used without instantiation or `await`.

**How to Fix:**
- Make `read_data_tool` a `@staticmethod` if it doesn't use `self`, or
- Always instantiate the class and use `await` when calling async methods, or
- Wrap the async method in a synchronous tool compatible with CrewAI.

---

### 4. Assigning Async Functions Directly to `tools`
**Bug:**
Async functions are assigned directly to `tools`, which is not supported.

**How to Fix:**
- Convert the function to synchronous if possible, or
- Use a wrapper that makes it compatible with CrewAI.

---

### 5. Unused Agent Roles
**Bug:**
Agents like `verifier`, `nutritionist`, `exercise_specialist` are defined but not added to the Crew.

**How to Fix:**
Add all relevant agents to the Crew's `agents` list.
```python
medical_crew = Crew(
    agents=[doctor, verifier, nutritionist, exercise_specialist],
    ...
)
```

---

### 6. Unused Tasks
**Bug:**
Tasks like `nutrition_analysis`, `exercise_planning`, `verification` are defined but not used.

**How to Fix:**
Add all relevant tasks to the Crew's `tasks` list.

---

### 7. Unrealistic/Satirical Agent Personalities
**Issue:**
Agents generate made-up or contradictory medical advice.

**How to Fix:**
Rewrite agent and task prompts to follow ethical AI and medical standards. Avoid generating false or misleading information.

---

### 8. Hardcoded File Path in `run_crew()`
**Bug:**
Used `"data/sample.pdf"` instead of the actual uploaded file path.

**How to Fix:**
Pass the correct `file_path` from the upload handler to `run_crew()`.

---

### 9. Unused Imports (e.g., `search_tool`)
**Bug:**
Imported but never used.

**How to Fix:**
Either attach the tool to an agent/task or remove the import.

---

### 10. Missing PDFLoader Import
**Bug:**
`PDFLoader` is used but not imported.

**How to Fix:**
Add the correct import:
```python
from langchain.document_loaders import PDFLoader
```

---

### 11. Incorrect Use of Class Methods in Tools
**Bug:**
Used `BloodTestReportTool.read_data_tool` directly.

**How to Fix:**
Instantiate the class and use the method properly, or make it a static/class method.

---

## 🟡 Functional & Code Quality Issues

- Merge duplicate import sections at the top of files.
- Use `uvicorn` CLI for running FastAPI in production.
- Rename methods for clarity (e.g., `read_data_tool` → `read_pdf_data`).
- Remove unused TODOs or implement them.
- Clarify task expectations to avoid contradictory instructions.
- Consistent agent delegation: Review `allow_delegation` settings.
- Add logging using Python's `logging` module for better debugging.
- Catch specific exceptions instead of broad `except Exception`.

---

## ✅ Optional Enhancements

- Add structured logging for all major actions and errors.
- Use environment variables for all sensitive keys and configuration.
- Write unit tests for all critical functions and endpoints.

---

**How to Overcome These Bugs:**
- Review all agent and tool definitions for correct parameters and instantiation.
- Refactor async/sync code for compatibility with your orchestration framework.
- Ensure all agents and tasks you define are actually used in the Crew.
- Regularly audit imports and remove unused code.
- Follow ethical guidelines for AI-generated content, especially in healthcare.
- Use dynamic file paths and user input, not hardcoded values.
- Add proper error handling and logging throughout the codebase.
