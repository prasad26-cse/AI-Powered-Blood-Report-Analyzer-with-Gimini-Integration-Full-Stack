#!/usr/bin/env python3
"""
Ultra-fast database clearing using direct MySQL connection
"""
import pymysql
import os
from dotenv import load_dotenv

def clear_database_fast():
    load_dotenv()
    
    # Get database credentials
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "Prasad")
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "bloodreport_ai")
    
    try:
        print("Connecting to MySQL...")
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        cursor = connection.cursor()
        
        print("Clearing database...")
        
        # Disable foreign key checks for faster deletion
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Truncate tables (much faster than DELETE)
        cursor.execute("TRUNCATE TABLE query_logs")
        print("✓ Cleared query_logs")
        
        cursor.execute("TRUNCATE TABLE blood_reports")
        print("✓ Cleared blood_reports")
        
        cursor.execute("TRUNCATE TABLE users")
        print("✓ Cleared users")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        connection.commit()
        print("✓ Database cleared successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    clear_database_fast() 