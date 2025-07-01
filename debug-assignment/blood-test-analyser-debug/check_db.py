#!/usr/bin/env python3
"""
Simple script to check database contents
"""

from database import SessionLocal, BloodReport

def check_database():
    db = SessionLocal()
    
    try:
        # Get all reports
        reports = db.query(BloodReport).all()
        print(f"Total reports in database: {len(reports)}")
        
        # Check for report ID 5
        report_5 = db.query(BloodReport).filter(BloodReport.id == 5).first()
        if report_5:
            print(f"Report 5 found: {report_5.filename}")
            print(f"  User ID: {report_5.user_id}")
            print(f"  File path: {report_5.file_path}")
            print(f"  Status: {report_5.processing_status}")
        else:
            print("Report 5 not found")
            
        # Show all report IDs
        print("\nAll available report IDs:")
        for report in reports:
            print(f"  ID {report.id}: {report.filename} (User: {report.user_id})")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_database() 