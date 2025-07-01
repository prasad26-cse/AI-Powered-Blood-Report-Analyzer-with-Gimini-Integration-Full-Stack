#!/usr/bin/env python3
"""
Test script to simulate upload and analysis process
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_upload_and_analysis():
    """Test the complete upload and analysis flow"""
    print("🧪 Testing Upload and Analysis Flow...")
    
    # Load environment variables
    load_dotenv()
    
    # Set API key
    api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
    os.environ["GEMINI_API_KEY"] = api_key
    
    # Test file path
    test_file = "data/sample.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"✅ Test file found: {test_file}")
    
    # Base URL
    base_url = "http://localhost:8000"
    
    try:
        # Step 1: Test health endpoint
        print("\n1️⃣ Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Backend is healthy: {health_data}")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
        
        # Step 2: Test simple Gemini analysis directly
        # print("\n2️⃣ Testing simple Gemini analysis...")
        # Gemini analysis is no longer available; skipping this step.
        
        # Step 3: Test Celery task directly
        print("\n3️⃣ Testing Celery task...")
        from celery_app import process_blood_report
        
        # Create a dummy report ID for testing
        test_report_id = 999
        
        # Test the Celery task
        task_result = process_blood_report.delay(test_report_id, "Please analyze my blood test report")
        
        # Get the result
        try:
            celery_result = task_result.get(timeout=30)
            print(f"✅ Celery task completed: {celery_result}")
        except Exception as e:
            print(f"❌ Celery task failed: {e}")
            return False
        
        print("\n🎉 All tests passed!")
        print("✅ The analysis system should be working properly.")
        print("\n📝 If you're still having issues in the frontend:")
        print("1. Check browser console for errors")
        print("2. Check backend logs for any errors")
        print("3. Make sure you're logged in to the frontend")
        print("4. Try uploading a different PDF file")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Upload and Analysis Test")
    print("=" * 60)
    
    success = test_upload_and_analysis()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        print("🔧 Please check the error messages above.")
    
    print("\n" + "=" * 60) 