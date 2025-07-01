from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import uuid
import asyncio
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

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

# Database setup with error handling
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    from sqlalchemy.orm import Session
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Prasad@localhost/bloodreport_ai")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    class User(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String(255), unique=True, index=True, nullable=False)
        username = Column(String(100), unique=True, index=True, nullable=False)
        hashed_password = Column(String(255), nullable=False)
        full_name = Column(String(200))
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        reports = relationship("BloodReport", back_populates="user")
        queries = relationship("QueryLog", back_populates="user")

    class BloodReport(Base):
        __tablename__ = "blood_reports"
        
        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
        filename = Column(String(255), nullable=False)
        file_path = Column(String(500), nullable=False)
        file_size = Column(Integer)
        upload_date = Column(DateTime, default=datetime.utcnow)
        processing_status = Column(String(50), default="pending")
        extracted_text = Column(Text)
        analysis_result = Column(Text)
        confidence_score = Column(Float)
        
        # Relationships
        user = relationship("User", back_populates="reports")
        queries = relationship("QueryLog", back_populates="report")

    class QueryLog(Base):
        __tablename__ = "query_logs"
        
        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
        report_id = Column(Integer, ForeignKey("blood_reports.id"), nullable=False)
        query_text = Column(Text, nullable=False)
        response_text = Column(Text)
        processing_time = Column(Float)
        status = Column(String(50), default="pending")
        created_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime)
        
        # Relationships
        user = relationship("User", back_populates="queries")
        report = relationship("BloodReport", back_populates="queries")

    # Create tables
    def create_tables():
        Base.metadata.create_all(bind=engine)

    # Dependency to get database session
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Initialize database
    create_tables()
    DATABASE_AVAILABLE = True
    
except Exception as e:
    print(f"Database setup failed: {e}")
    DATABASE_AVAILABLE = False
    # Create dummy functions for when database is not available
    def get_db_fallback():
        yield None
    
    UserModel: Any = None
    BloodReportModel: Any = None
    QueryLogModel: Any = None

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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db if DATABASE_AVAILABLE else get_db_fallback)):
    if not DATABASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def run_crew(query: str, file_path: str):
    """Runs the complete medical analysis Crew process."""
    try:
        from crewai import Crew, Process
        from agents import doctor, verifier, nutritionist, exercise_specialist
        from task import create_help_patients_task
        
        # Create task with doctor agent
        help_patients_task = create_help_patients_task(doctor)
        
        medical_crew = Crew(
            agents=[doctor, verifier, nutritionist, exercise_specialist],
            tasks=[help_patients_task],
            process=Process.sequential
        )
        
        return medical_crew.kickoff(inputs={"query": query, "file_path": file_path})
    except Exception as e:
        return f"Error in analysis: {str(e)}"

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

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "database_available": DATABASE_AVAILABLE
    }

@app.get("/api/status")
async def api_status():
    """Get API status and available features"""
    return {
        "status": "running",
        "database": "available" if DATABASE_AVAILABLE else "unavailable",
        "features": {
            "authentication": DATABASE_AVAILABLE,
            "file_upload": True,
            "ai_analysis": True
        }
    } 