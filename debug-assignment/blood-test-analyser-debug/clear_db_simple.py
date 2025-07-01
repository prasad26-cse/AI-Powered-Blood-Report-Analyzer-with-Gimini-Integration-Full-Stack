#!/usr/bin/env python3
"""
Simple script to clear all data from the database quickly
"""
from database import SessionLocal
from sqlalchemy import text

def clear_database_simple():
    db = SessionLocal()
    try:
        print("Clearing database...")
        
        # Delete all data from tables
        db.execute(text("DELETE FROM query_logs"))
        print("✓ Cleared query_logs")
        
        db.execute(text("DELETE FROM blood_reports"))
        print("✓ Cleared blood_reports")
        
        db.execute(text("DELETE FROM users"))
        print("✓ Cleared users")
        
        # Reset auto-increment counters
        db.execute(text("ALTER TABLE query_logs AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE blood_reports AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE users AUTO_INCREMENT = 1"))
        
        db.commit()
        print("✓ Database cleared successfully!")
        print("✓ Auto-increment counters reset")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_database_simple() 