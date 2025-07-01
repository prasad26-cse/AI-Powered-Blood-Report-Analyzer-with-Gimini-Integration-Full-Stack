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
