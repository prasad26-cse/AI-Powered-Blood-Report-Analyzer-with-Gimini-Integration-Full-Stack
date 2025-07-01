from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import uuid
import asyncio
from typing import Optional, Any, Generator
from dotenv import load_dotenv
import io
import PyPDF2

# Try to import database components, but handle gracefully if they fail
try:
    from database import get_db, User, BloodReport, QueryLog, create_tables
    DATABASE_AVAILABLE = True
except Exception as e:
    print(f"Database not available: {e}")
    DATABASE_AVAILABLE = False
    def create_tables():
        pass

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

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

# Create database tables
create_tables()

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not DATABASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        username = str(username)  # Explicit type cast after None check
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register a new user"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User registered successfully", "user_id": user.id}

@app.post("/api/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """Endpoint to analyze uploaded blood test PDF report (in-memory, fast)"""
    try:
        content = await file.read()
        # Save content to temporary file
        temp_file_path = f"data/temp_{uuid.uuid4()}.pdf"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)
        
        # Run analysis in a thread to avoid blocking
        from enhanced_analysis import enhanced_simple_blood_analysis
        result = await asyncio.to_thread(enhanced_simple_blood_analysis, temp_file_path, query.strip())
        
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        # Always return a structured analysis result
        if isinstance(result, dict):
            analysis_result = result.get("result", "No analysis result was generated.")
            fallback = result.get("fallback", False)
            status = result.get("status", "processed")
        else:
            analysis_result = str(result)
            fallback = True
            status = "error"
        return {
            "status": status,
            "query": query.strip(),
            "result": analysis_result,
            "fallback": fallback,
            "file_processed": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")

@app.get("/api/user-reports")
async def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports for current user"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    reports = db.query(BloodReport).filter(
        BloodReport.user_id == current_user.id
    ).order_by(BloodReport.upload_date.desc()).all()
    
    return [
        {
            "id": report.id,
            "filename": report.filename,
            "upload_date": report.upload_date,
            "processing_status": report.processing_status,
            "confidence_score": report.confidence_score
        }
        for report in reports
    ]

@app.get("/api/report/{report_id}")
async def get_report_details(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed report information"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    report = db.query(BloodReport).filter(
        BloodReport.id == report_id,
        BloodReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": report.id,
        "filename": report.filename,
        "upload_date": report.upload_date,
        "processing_status": report.processing_status,
        "analysis_result": report.analysis_result,
        "confidence_score": report.confidence_score,
        "extracted_text": report.extracted_text
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Add run_crew function for analysis
def run_crew(query: str, file_path: str):
    """Runs the complete medical analysis Crew process."""
    try:
        from crewai import Crew, Process
        from agents import GEMINI_AVAILABLE, doctor, verifier, nutritionist, exercise_specialist
        from task import create_help_patients_task
        # Check if Gemini is available before creating Crew
        if not GEMINI_AVAILABLE:
            return {"status": "error", "result": "Gemini AI is not available. Please check your API key configuration.", "fallback": True}
        # Create task with doctor agent
        help_patients_task = create_help_patients_task(doctor)
        # At this point, agents are guaranteed to be proper BaseAgent instances
        medical_crew = Crew(
            agents=[doctor, verifier, nutritionist, exercise_specialist],  # type: ignore
            tasks=[help_patients_task],
            process=Process.sequential
        )
        result = medical_crew.kickoff(inputs={"query": query, "file_path": file_path})
        print(f"[run_crew] Raw CrewAI result: {result}")  # Debug log
        # If result is empty or None, return fallback
        if not result or (isinstance(result, str) and not result.strip()):
            return {"status": "error", "result": "No analysis result was generated. Please try again.", "fallback": True}
        return {"status": "processed", "result": str(result), "fallback": False}
    except Exception as e:
        return {"status": "error", "result": f"Error in analysis: {str(e)}", "fallback": True}

# Server startup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
