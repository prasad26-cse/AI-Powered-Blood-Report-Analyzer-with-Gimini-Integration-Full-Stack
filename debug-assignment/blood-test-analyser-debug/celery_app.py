from datetime import datetime
import time
import os
from celery import Celery
from dotenv import load_dotenv
from database import SessionLocal, BloodReport, QueryLog

load_dotenv()

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "memory://")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

celery_app = Celery(
    "bloodreport_ai",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,  # Prevent worker from prefetching too many tasks
    task_acks_late=True,  # Only acknowledge task completion after successful execution
    # Windows-specific settings
    worker_pool_restarts=True,
    worker_max_tasks_per_child=1,  # Restart worker after each task on Windows
    worker_disable_rate_limits=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    # Use solo pool for Windows compatibility
    worker_pool='solo',
)

@celery_app.task(bind=True)
def process_blood_report(self, report_id: int, query_text: str):
    """Process blood report asynchronously using Simple Gemini AI or fallback"""
    start_time = time.time()
    db = None
    report = None
    
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Processing blood report...'})
        
        # Get database session
        db = SessionLocal()
        
        # Get the blood report
        report = db.query(BloodReport).filter(BloodReport.id == report_id).first()
        if not report:
            raise Exception(f"Blood report with ID {report_id} not found")
        
        # Ensure the uploaded file exists before analysis
        if not os.path.exists(str(report.file_path)):
            raise Exception(f"Uploaded file not found: {report.file_path}. Please upload a valid PDF file from the frontend.")
        
        # Update report status
        setattr(report, 'processing_status', "processing")  # type: ignore
        db.commit()
        
        # Check if Gemini AI is available
        try:
            from enhanced_analysis import enhanced_simple_blood_analysis
            load_dotenv()
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            if GEMINI_API_KEY:
                print("[CELERY] Using enhanced Gemini AI analysis...")
                result = enhanced_enhanced_simple_blood_analysis(str(report.file_path), query_text)
                if result["status"] == "processed" and not result.get("fallback", True):
                    print("[CELERY] Enhanced Gemini analysis completed successfully!")
                else:
                    print("[CELERY] Enhanced Gemini analysis failed, using fallback...")
                    result = enhanced_enhanced_simple_blood_analysis(str(report.file_path), query_text)
            else:
                print("[CELERY] Gemini API key not found. Using fallback analysis.")
                result = enhanced_enhanced_simple_blood_analysis(str(report.file_path), query_text)
        except Exception as ai_error:
            print(f"[CELERY] Enhanced Gemini analysis failed: {ai_error}")
            print("[CELERY] Falling back to simple analysis due to error above.")
            result = enhanced_enhanced_simple_blood_analysis(str(report.file_path), query_text)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update report with results
        setattr(report, 'processing_status', "completed")  # type: ignore
        if isinstance(result, dict) and "result" in result:
            setattr(report, 'analysis_result', result["result"])  # type: ignore
        else:
            setattr(report, 'analysis_result', str(result))  # type: ignore
        setattr(report, 'confidence_score', 0.95 if not result.get("fallback", True) else 0.85)  # type: ignore
        db.commit()
        
        # Create query log entry
        query_log = QueryLog(
            user_id=report.user_id,
            report_id=report.id,
            query_text=query_text,
            response_text=str(result),
            processing_time=processing_time,
            status="completed",
            completed_at=datetime.utcnow()
        )
        db.add(query_log)
        db.commit()
        
        return {
            'status': 'completed',
            'result': str(result),
            'processing_time': processing_time,
            'report_id': report_id
        }
        
    except Exception as e:
        # Update status on error
        try:
            if db and report:
                setattr(report, 'processing_status', "failed")
                db.commit()
        except Exception as db_error:
            print(f"[CELERY] Error updating report status: {db_error}")
        
        # Create failed query log only if we have a valid report
        try:
            if db and report:
                query_log = QueryLog(
                    user_id=report.user_id,
                    report_id=report_id,
                    query_text=query_text,
                    response_text=f"Error: {str(e)}",
                    processing_time=time.time() - start_time,
                    status="failed",
                    completed_at=datetime.utcnow()
                )
                db.add(query_log)
                db.commit()
        except Exception as log_error:
            print(f"[CELERY] Error creating query log: {log_error}")
        
        raise Exception(f"Failed to process blood report: {str(e)}")
    
    finally:
        try:
            if db:
                db.close()
        except:
            pass

# Simple fallback analysis function
def simple_blood_analysis(file_path: str, query: str) -> dict:
    """Simple fallback analysis without external AI services"""
    try:
        # Basic analysis based on query keywords
        query_lower = query.lower()
        
        # Attempt to get user's full name from the report
        from database import SessionLocal, BloodReport
        db = SessionLocal()
        report = db.query(BloodReport).filter(BloodReport.file_path == file_path).first()
        user_name = None
        if report and report.user and report.user.full_name:
            user_name = report.user.full_name
        elif report and report.user and report.user.username:
            user_name = report.user.username
        else:
            user_name = "User"
        db.close()
        
        if "summarize" in query_lower or "summary" in query_lower:
            result = f"Blood Test Report Summary for {user_name}:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nKey points:\n- Your report has been successfully uploaded and stored\n- All standard blood test parameters are included\n- The report is ready for detailed analysis when the service is restored\n\nPlease try the analysis again in a few minutes for a comprehensive AI-powered review of your results."
        elif "concerning" in query_lower or "abnormal" in query_lower:
            result = f"Blood Test Analysis - Concerning Values for {user_name}:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nNote: This is a basic response. For detailed analysis of concerning values, please:\n- Try the analysis again in a few minutes\n- Consult with your healthcare provider\n- Review the report values against standard reference ranges\n\nYour report has been successfully uploaded and is ready for detailed analysis."
        elif "meaning" in query_lower or "explain" in query_lower:
            result = f"Blood Test Results Explanation for {user_name}:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nYour blood test report contains standard laboratory values that need to be interpreted in the context of:\n- Your medical history\n- Current symptoms\n- Reference ranges for your age and gender\n- Previous test results\n\nPlease try the analysis again in a few minutes for a detailed AI-powered explanation of your specific results."
        else:
            result = f"Blood Test Analysis for {user_name}:\n\nThis is a fallback analysis for your blood test report. The AI analysis service is currently unavailable.\n\nYour query: '{query}'\n\nResponse: Your blood test report has been successfully uploaded and is ready for analysis. Please try again in a few minutes for a comprehensive AI-powered review of your results.\n\nIn the meantime, you can:\n- Review the raw values in your report\n- Compare with standard reference ranges\n- Consult with your healthcare provider for interpretation"
        
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

@celery_app.task
def extract_pdf_text(report_id: int):
    """Extract text from uploaded PDF"""
    try:
        db = SessionLocal()
        report = db.query(BloodReport).filter(BloodReport.id == report_id).first()
        
        if not report:
            raise Exception("Report not found")
        
        # Extract text from PDF
        from tools import BloodTestReportTool
        pdf_tool = BloodTestReportTool()
        extracted_text = pdf_tool.read_data_tool(str(report.file_path))
        
        # Update report with extracted text
        setattr(report, 'extracted_text', extracted_text)  # type: ignore
        db.commit()
        
        return {"status": "success", "extracted_text": extracted_text}
        
    except Exception as e:
        raise Exception(f"Failed to extract PDF text: {str(e)}")
    
    finally:
        try:
            db.close()
        except:
            pass 