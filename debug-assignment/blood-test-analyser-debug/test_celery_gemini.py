#!/usr/bin/env python3
"""
Test script to verify Celery task with simple Gemini analysis
"""

import os
from dotenv import load_dotenv
from celery_app import process_blood_report

def test_celery_gemini():
    """Test Celery task with simple Gemini analysis"""
    print("🧪 Testing Celery Task with Simple Gemini Analysis...")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Fallback API key if not found
    if not api_key:
        api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
        os.environ["GEMINI_API_KEY"] = api_key
        print("⚠️  Using fallback API key")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    # Test file path
    test_file = "data/sample.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"✅ Test file found: {test_file}")
    print("🔍 Running Celery task with simple Gemini analysis...")
    
    try:
        # Run the Celery task
        result = process_blood_report.delay(1, "Please analyze my blood test report and provide a summary")
        
        # Wait for result
        analysis_result = result.get(timeout=60)
        
        print("✅ Celery task completed successfully!")
        print("📊 Analysis Result:")
        print("=" * 50)
        print(analysis_result)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Celery task failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Celery + Simple Gemini Analysis Test")
    print("=" * 60)
    
    success = test_celery_gemini()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("✅ Your Celery worker with simple Gemini analysis is working!")
    else:
        print("\n❌ Test failed!")
        print("🔧 Please check the error messages above.")
    
    print("\n" + "=" * 60) 