from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import uuid
import asyncio
import time
import logging
from typing import Optional, Any, Dict
from dotenv import load_dotenv
from functools import lru_cache
import redis
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import database components, but handle gracefully if they fail
try:
    from database import get_db, User, BloodReport, QueryLog, create_tables
    DATABASE_AVAILABLE = True
except Exception as e:
    logger.warning(f"Database not available: {e}")
    DATABASE_AVAILABLE = False
    # Create dummy functions for when database is not available
    def get_db() -> Any:
        yield None
    
    def create_tables():
        pass

try:
    from celery_app import process_blood_report, extract_pdf_text
    CELERY_AVAILABLE = True
except Exception as e:
    logger.warning(f"Celery not available: {e}")
    CELERY_AVAILABLE = False
    def process_blood_report(*args, **kwargs):
        return {"status": "celery_not_available"}
    def extract_pdf_text(*args, **kwargs):
        return {"status": "celery_not_available"}

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Redis configuration for caching
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    REDIS_AVAILABLE = False
    redis_client = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.request_times = {}
    
    def start_timer(self, endpoint: str):
        self.request_times[endpoint] = time.time()
    
    def end_timer(self, endpoint: str) -> float:
        if endpoint in self.request_times:
            duration = time.time() - self.request_times[endpoint]
            logger.info(f"{endpoint} took {duration:.3f}s")
            return duration
        return 0.0

performance_monitor = PerformanceMonitor()

app = FastAPI(
    title="BloodReport AI - Optimized", 
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware with optimized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Create database tables
create_tables()

# Cache configuration
CACHE_TTL = 300  # 5 minutes default TTL

def get_cache_key(prefix: str, identifier: str) -> str:
    """Generate a cache key"""
    return f"{prefix}:{identifier}"

def get_cached_data(key: str) -> Optional[Any]:
    """Get data from cache"""
    if not REDIS_AVAILABLE or redis_client is None:
        return None
    try:
        data = redis_client.get(key)
        if data is None:
            return None
        if isinstance(data, str):
            return json.loads(data)
        return data
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return None

def set_cached_data(key: str, data: Any, ttl: int = CACHE_TTL) -> bool:
    """Set data in cache"""
    if not REDIS_AVAILABLE or redis_client is None:
        return False
    try:
        redis_client.setex(key, ttl, json.dumps(data))
        return True
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
        return False

def delete_cached_data(key: str) -> bool:
    """Delete data from cache"""
    if not REDIS_AVAILABLE or redis_client is None:
        return False
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")
        return False

# Authentication functions with caching
@lru_cache(maxsize=128)
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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
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
        username = str(username)
    except JWTError:
        raise credentials_exception
    
    # Try to get user from cache first
    cache_key = get_cache_key("user", username)
    cached_user = get_cached_data(cache_key)
    
    if cached_user:
        return User(**cached_user)
    
    # If not in cache, query database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # Cache user data
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "full_name": user.full_name,
        "hashed_password": user.hashed_password
    }
    set_cached_data(cache_key, user_data, ttl=600)  # Cache for 10 minutes
    
    return user

# API Routes with performance monitoring
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} took {process_time:.3f}s")
    return response

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI page."""
    performance_monitor.start_timer("root")
    try:
        response = templates.TemplateResponse("index.html", {"request": request})
        performance_monitor.end_timer("root")
        return response
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    mobile_number: str = Form(default=""),
    password: str = Form(...),
    full_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register a new user with optimized validation"""
    performance_monitor.start_timer("register")
    
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Check if user already exists (optimized query)
        existing_user = db.query(User.id).filter(
            (User.username == username) | (User.email == email) | 
            (User.mobile_number == mobile_number if mobile_number else False)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username, email, or mobile number already registered")
        
        # Create new user
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            mobile_number=mobile_number if mobile_number else None,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Clear any cached user data
        if REDIS_AVAILABLE:
            cache_key = get_cache_key("user", username)
            delete_cached_data(cache_key)
        
        performance_monitor.end_timer("register")
        return {"message": "User registered successfully", "user_id": user.id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/login")
async def login(
    identifier: str = Form(...),  # Changed from username to identifier
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login user with username, email, or mobile number and return access token with caching"""
    performance_monitor.start_timer("login")
    
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Try to get user from cache first
        cache_key = get_cache_key("user", identifier)
        cached_user = get_cached_data(cache_key)
        
        if cached_user:
            user = User(**cached_user)
        else:
            # Try to find user by username, email, or mobile number
            user = db.query(User).filter(
                (User.username == identifier) | 
                (User.email == identifier) | 
                (User.mobile_number == identifier)
            ).first()
            
            if user:
                # Cache user data
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "mobile_number": user.mobile_number,
                    "full_name": user.full_name,
                    "hashed_password": user.hashed_password
                }
                set_cached_data(cache_key, user_data, ttl=600)
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect credentials")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        performance_monitor.end_timer("login")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "mobile_number": user.mobile_number,
                "full_name": user.full_name
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/upload-report")
async def upload_blood_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload blood test report PDF with optimized file handling"""
    performance_monitor.start_timer("upload_report")
    
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"blood_test_report_{file_id}.pdf"
        file_path = os.path.join("data", filename)
        
        # Save file asynchronously
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create database record
        report = BloodReport(
            user_id=current_user.id,
            filename=filename,
            file_path=file_path,
            upload_date=datetime.utcnow(),
            processing_status="uploaded"
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Clear user reports cache
        if REDIS_AVAILABLE:
            cache_key = get_cache_key("user_reports", str(current_user.id))
            delete_cached_data(cache_key)
        
        performance_monitor.end_timer("upload_report")
        return {
            "message": "Report uploaded successfully",
            "report_id": report.id,
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Upload failed")

@app.post("/api/analyze-report-sync")
async def analyze_blood_report_sync(
    report_id: int = Form(...),
    query: str = Form(default="Summarise my Blood Test Report"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Synchronous analysis with caching and better error handling"""
    performance_monitor.start_timer("analyze_sync")
    
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Check cache first
        cache_key = get_cache_key("analysis", f"{report_id}_{hash(query)}")
        cached_result = get_cached_data(cache_key)
        
        if cached_result:
            performance_monitor.end_timer("analyze_sync")
            return cached_result
        
        # Get report
        report = db.query(BloodReport).filter(
            BloodReport.id == report_id,
            BloodReport.user_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Process report with better error handling
        try:
            if CELERY_AVAILABLE:
                result = process_blood_report.delay(report.id, query)
                analysis_result = result.get(timeout=15)  # Reduced timeout to 15 seconds
            else:
                # Fallback to simple analysis
                analysis_result = simple_blood_analysis(str(report.file_path), query)
        except Exception as celery_error:
            logger.warning(f"Celery processing failed: {celery_error}")
            # Use simple fallback analysis
            analysis_result = simple_blood_analysis(str(report.file_path), query)
        
        # Update report status and analysis result
        # Type: ignore comments added because SQLAlchemy model attributes can be assigned values
        report.processing_status = "completed"  # type: ignore
        if isinstance(analysis_result, dict) and "result" in analysis_result:
            report.analysis_result = analysis_result["result"]  # type: ignore
        else:
            report.analysis_result = str(analysis_result)  # type: ignore
        report.confidence_score = 0.85  # type: ignore # Default confidence for fallback analysis
        db.commit()
        
        # Cache result
        set_cached_data(cache_key, analysis_result, ttl=1800)  # Cache for 30 minutes
        
        # Log query
        query_log = QueryLog(
            user_id=current_user.id,
            report_id=report_id,
            query_text=query
        )
        db.add(query_log)
        db.commit()
        
        performance_monitor.end_timer("analyze_sync")
        return analysis_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze-report")
async def analyze_blood_report(
    report_id: int = Form(...),
    query: str = Form(default="Summarise my Blood Test Report"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Asynchronous analysis with task queue"""
    performance_monitor.start_timer("analyze_async")
    
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get report
        report = db.query(BloodReport).filter(
            BloodReport.id == report_id,
            BloodReport.user_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Submit task
        if CELERY_AVAILABLE:
            task = process_blood_report.delay(report.id, query)
            task_id = task.id
        else:
            task_id = "celery_not_available"
        
        # Log query
        query_log = QueryLog(
            user_id=current_user.id,
            report_id=report_id,
            query_text=query
        )
        db.add(query_log)
        db.commit()
        
        performance_monitor.end_timer("analyze_async")
        return {"task_id": task_id, "status": "processing"}
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get task status with caching"""
    performance_monitor.start_timer("task_status")
    
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available")
    
    try:
        # Check cache first
        cache_key = get_cache_key("task_status", task_id)
        cached_status = get_cached_data(cache_key)
        
        if cached_status:
            performance_monitor.end_timer("task_status")
            return cached_status
        
        # Get task status
        task = process_blood_report.AsyncResult(task_id)
        status_data = {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None
        }
        
        # Cache status for 30 seconds
        set_cached_data(cache_key, status_data, ttl=30)
        
        performance_monitor.end_timer("task_status")
        return status_data
    
    except Exception as e:
        logger.error(f"Task status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task status")

@app.get("/api/user-reports")
async def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user reports with caching"""
    performance_monitor.start_timer("user_reports")
    
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Check cache first
        cache_key = get_cache_key("user_reports", str(current_user.id))
        cached_reports = get_cached_data(cache_key)
        
        if cached_reports:
            performance_monitor.end_timer("user_reports")
            return cached_reports
        
        # Query database
        reports = db.query(BloodReport).filter(
            BloodReport.user_id == current_user.id
        ).order_by(BloodReport.upload_date.desc()).all()
        
        reports_data = [
            {
                "id": report.id,
                "filename": report.filename,
                "upload_date": report.upload_date.isoformat(),
                "status": report.processing_status,
                "analysis_result": report.analysis_result,
                "confidence_score": report.confidence_score
            }
            for report in reports
        ]
        
        # Cache reports for 5 minutes
        set_cached_data(cache_key, reports_data, ttl=300)
        
        performance_monitor.end_timer("user_reports")
        return reports_data
    
    except Exception as e:
        logger.error(f"User reports error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reports")

@app.get("/api/report/{report_id}")
async def get_report_details(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report details with caching"""
    performance_monitor.start_timer("report_details")
    
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Check cache first
        cache_key = get_cache_key("report_details", str(report_id))
        cached_report = get_cached_data(cache_key)
        
        if cached_report:
            performance_monitor.end_timer("report_details")
            return cached_report
        
        # Query database
        report = db.query(BloodReport).filter(
            BloodReport.id == report_id,
            BloodReport.user_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_data = {
            "id": report.id,
            "filename": report.filename,
            "upload_date": report.upload_date.isoformat(),
            "status": report.processing_status,
            "file_path": report.file_path,
            "analysis_result": report.analysis_result,
            "confidence_score": report.confidence_score
        }
        
        # Cache report details for 10 minutes
        set_cached_data(cache_key, report_data, ttl=600)
        
        performance_monitor.end_timer("report_details")
        return report_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report details error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report details")

@app.delete("/api/report/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a blood report with authentication confirmation"""
    performance_monitor.start_timer("delete_report")
    logger.info(f"Attempting to delete report_id={report_id} for user_id={current_user.id}")

    if not DATABASE_AVAILABLE:
        logger.error("Database not available")
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # Get report and verify ownership
        report = db.query(BloodReport).filter(
            BloodReport.id == report_id,
            BloodReport.user_id == current_user.id
        ).first()
        if not report:
            logger.warning(f"Report not found: id={report_id} user_id={current_user.id}")
            raise HTTPException(status_code=404, detail="Report not found")

        logger.info(f"Found report: {report.filename}, file_path={report.file_path}")

        # Delete the physical file if it exists
        if getattr(report, "file_path", None):
            if os.path.exists(str(report.file_path)):
                try:
                    os.remove(str(report.file_path))
                    logger.info(f"Deleted file: {report.file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete file {report.file_path}: {e}")
            else:
                logger.warning(f"File does not exist: {report.file_path}")
        else:
            logger.warning(f"No file_path for report id={report_id}")

        # Delete from database
        db.delete(report)
        db.commit()
        logger.info(f"Deleted report from database: id={report_id}")

        # Clear caches
        if REDIS_AVAILABLE:
            # Clear user reports cache
            cache_key_user = get_cache_key("user_reports", str(current_user.id))
            delete_cached_data(cache_key_user)
            logger.info(f"Deleted user_reports cache: {cache_key_user}")
            # Clear report details cache
            cache_key_report = get_cache_key("report_details", str(report_id))
            delete_cached_data(cache_key_report)
            logger.info(f"Deleted report_details cache: {cache_key_report}")

        performance_monitor.end_timer("delete_report")
        return {"message": "Report deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete report error (id={report_id}): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete report")

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": DATABASE_AVAILABLE,
            "celery": CELERY_AVAILABLE,
            "redis": REDIS_AVAILABLE
        },
        "version": "2.0.0"
    }

@app.get("/api/performance")
async def get_performance_stats():
    """Get performance statistics"""
    return {
        "cache_hits": get_cached_data("cache_stats:hits") or 0,
        "cache_misses": get_cached_data("cache_stats:misses") or 0,
        "redis_available": REDIS_AVAILABLE,
        "database_available": DATABASE_AVAILABLE,
        "celery_available": CELERY_AVAILABLE
    }

# Enhanced analysis function using Gemini AI
def simple_blood_analysis(file_path: str, query: str) -> dict:
    """Enhanced analysis using Gemini AI with fallback"""
    try:
        import google.generativeai as genai
        from google.generativeai.generative_models import GenerativeModel
        import PyPDF2
        
        # Set API key
        api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
        genai.configure(api_key=api_key)
        
        # Create model
        model = GenerativeModel('gemini-1.5-flash')
        
        # Extract text from PDF
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
        except Exception as e:
            print(f"PDF reading error: {e}")
            text_content = "Blood test report content could not be extracted from PDF."
        
        # Create analysis prompt
        analysis_prompt = f"""
        You are a medical AI assistant. Please analyze this blood test report and provide a comprehensive analysis.
        
        User Query: {query}
        
        Blood Test Report Content:
        {text_content[:3000]}  # Limit content length
        
        Please provide your analysis in this structured format:
        
        **1. Summary of Key Findings**
        [Provide a brief overview of the blood test results]
        
        **2. Interpretation of Any Abnormal Values**
        [Explain any values that are outside normal ranges]
        
        **3. Clinical Significance of Results**
        [Discuss the medical implications of the findings]
        
        **4. Recommendations for Follow-up**
        [Provide specific recommendations for the patient]
        
        **5. Overall Health Assessment**
        [Give an overall assessment of the patient's health based on these results]
        
        Please be thorough, professional, and provide actionable insights.
        """
        
        # Generate analysis
        response = model.generate_content(analysis_prompt)
        
        return {
            "status": "processed",
            "result": response.text,
            "fallback": False,
            "confidence_score": 0.95
        }
        
    except Exception as e:
        print(f"Enhanced analysis error: {e}")
        # Fallback to basic analysis
        query_lower = query.lower()
        
        if "summarize" in query_lower or "summary" in query_lower:
            result = f"Blood Test Report Summary:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nKey points:\n- Your report has been successfully uploaded and stored\n- All standard blood test parameters are included\n- The report is ready for detailed analysis when the service is restored\n\nPlease try the analysis again in a few minutes for a comprehensive AI-powered review of your results."
        elif "concerning" in query_lower or "abnormal" in query_lower:
            result = f"Blood Test Analysis - Concerning Values:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nNote: This is a basic response. For detailed analysis of concerning values, please:\n- Try the analysis again in a few minutes\n- Consult with your healthcare provider\n- Review the report values against standard reference ranges\n\nYour report has been successfully uploaded and is ready for detailed analysis."
        elif "meaning" in query_lower or "explain" in query_lower:
            result = f"Blood Test Results Explanation:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nYour blood test report contains standard laboratory values that need to be interpreted in the context of:\n- Your medical history\n- Current symptoms\n- Reference ranges for your age and gender\n- Previous test results\n\nPlease try the analysis again in a few minutes for a detailed AI-powered explanation of your specific results."
        else:
            result = f"Blood Test Analysis:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nYour query: '{query}'\n\nResponse: Your blood test report has been successfully uploaded and is ready for analysis. Please try again in a few minutes for a comprehensive AI-powered review of your results.\n\nIn the meantime, you can:\n- Review the raw values in your report\n- Compare with standard reference ranges\n- Consult with your healthcare provider for interpretation"
        
        return {
            "status": "processed",
            "result": result,
            "fallback": True
        }
    except Exception as e:
        return {
            "status": "processed",
            "result": f"Fallback analysis completed. Your report has been uploaded successfully. Please try the AI analysis again in a few minutes. Error: {str(e)}",
            "fallback": True
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
        log_level="info"
    ) 