#!/usr/bin/env python3
"""
Script to clear all data from the main tables in the database.
"""
from database import SessionLocal, User, BloodReport
from sqlalchemy import text

def clear_database():
    db = SessionLocal()
    try:
        # Disable foreign key checks (for MySQL)
        db.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        db.commit()
        # Truncate tables
        db.execute(text('TRUNCATE TABLE query_logs;'))
        db.execute(text('TRUNCATE TABLE blood_reports;'))
        db.execute(text('TRUNCATE TABLE users;'))
        db.commit()
        # Re-enable foreign key checks
        db.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        db.commit()
        print('All data cleared from users, blood_reports, and query_logs tables.')
    finally:
        db.close()

if __name__ == "__main__":
    clear_database() 