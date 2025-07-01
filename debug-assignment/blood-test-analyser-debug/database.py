from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
import pymysql

# Register PyMySQL as the MySQL driver
pymysql.install_as_MySQLdb()

load_dotenv()

# Database configuration with environment variables
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "bloodreport_ai")

# Construct database URL
if DB_PASSWORD:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Fallback to SQLite if MySQL is not available
if not all([DB_USER, DB_HOST]):
    DATABASE_URL = "sqlite:///./bloodreport_ai.db"
    print("Using SQLite as fallback database")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    mobile_number = Column(String(20), unique=True, index=True, nullable=True)
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
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    extracted_text = Column(Text)
    analysis_result = Column(Text)
    confidence_score = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    queries = relationship("QueryLog", back_populates="report", cascade="all, delete-orphan", passive_deletes=True)

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("blood_reports.id", ondelete="CASCADE"), nullable=False)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    processing_time = Column(Float)  # in seconds
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="queries")
    report = relationship("BloodReport", back_populates="queries", passive_deletes=True)

# Create tables
def create_tables():
    global engine, SessionLocal
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # Try with SQLite as fallback
        if "mysql" in DATABASE_URL.lower():
            print("Falling back to SQLite database...")
            engine = create_engine("sqlite:///./bloodreport_ai.db")
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)
            print("SQLite database created successfully")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 