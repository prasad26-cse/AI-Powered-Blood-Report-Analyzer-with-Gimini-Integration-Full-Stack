#!/usr/bin/env python3
"""
Optimized Blood Test Analyzer Startup Script
This script starts the optimized FastAPI server with proper configuration.
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import redis
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install missing packages: pip install fastapi uvicorn redis")
        return False

def start_redis():
    """Start Redis server if not running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis is already running")
        return True
    except:
        print("⚠ Redis is not running. Starting Redis...")
        try:
            # Try to start Redis (Windows)
            subprocess.Popen(["redis-server"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            time.sleep(2)
            print("✓ Redis started successfully")
            return True
        except:
            print("✗ Failed to start Redis. Continuing without caching...")
            return False

def main():
    """Main startup function"""
    print("🚀 Starting Optimized Blood Test Analyzer...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start Redis
    start_redis()
    
    # Set environment variables
    os.environ.setdefault("SECRET_KEY", "your-secret-key-here")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
    
    print("\n📡 Starting FastAPI server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "main_optimized:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 