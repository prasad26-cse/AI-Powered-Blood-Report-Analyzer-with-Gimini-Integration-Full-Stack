from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BloodReport AI", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

try:
    from crewai import Crew, Process
except ImportError:
    raise RuntimeError("crewai package is not installed. Please install it with 'pip install crewai'")

def run_crew(query: str, file_path: str):
    """Runs the complete medical analysis Crew process."""
    try:
        from agents import doctor, verifier, nutritionist, exercise_specialist
        from task import create_help_patients_task
        
        # Create task with doctor agent
        help_patients_task = create_help_patients_task(doctor)
        
        medical_crew = Crew(
            agents=[doctor, verifier, nutritionist, exercise_specialist],
            tasks=[help_patients_task],
            process=Process.sequential
        )
        
        # CrewAI's kickoff method requires input values like file_path and query
        return medical_crew.kickoff(inputs={"query": query, "file_path": file_path})
    except Exception as e:
        return f"Error in analysis: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """Endpoint to analyze uploaded blood test PDF report"""
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        if not query.strip():
            query = "Summarise my Blood Test Report"
        
        # Run crew in a separate thread to avoid blocking FastAPI event loop
        result = await asyncio.to_thread(run_crew, query.strip(), file_path)
        
        return {
            "status": "success",
            "query": query.strip(),
            "analysis": str(result),
            "file_processed": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "BloodReport AI is running"} 