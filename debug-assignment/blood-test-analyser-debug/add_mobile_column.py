from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import pymysql

# Register PyMySQL as the MySQL driver
pymysql.install_as_MySQLdb()

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Prasad@localhost/bloodreport_ai")

engine = create_engine(DATABASE_URL)

def add_mobile_column():
    """Add mobile_number column to users table if it doesn't exist"""
    try:
        with engine.connect() as connection:
            # Check if mobile_number column exists
            result = connection.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'bloodreport_ai' 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'mobile_number'
            """))
            
            if not result.fetchone():
                # Add mobile_number column
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN mobile_number VARCHAR(20) UNIQUE NULL
                """))
                connection.commit()
                print("✅ mobile_number column added successfully!")
            else:
                print("✅ mobile_number column already exists!")
                
    except Exception as e:
        print(f"❌ Error adding mobile_number column: {e}")

if __name__ == "__main__":
    add_mobile_column() 