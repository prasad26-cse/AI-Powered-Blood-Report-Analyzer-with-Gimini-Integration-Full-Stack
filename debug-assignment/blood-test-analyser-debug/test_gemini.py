#!/usr/bin/env python3
"""
Test script for Gemini AI integration
"""

print("[DEBUG] test_gemini.py started")

import os
from dotenv import load_dotenv
print("[DEBUG] Imported os and dotenv")
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel  # type: ignore
print("[DEBUG] Imported GenerativeModel")

def test_gemini_connection():
    print("[DEBUG] test_gemini_connection called")
    """Test if Gemini AI is properly configured and accessible"""
    
    # Load environment variables with error handling
    try:
        load_dotenv()
        print("[DEBUG] Loaded .env")
    except Exception as e:
        print(f"[DEBUG] Warning: Could not load .env file: {e}")
        print("[DEBUG] Trying to get API key from environment variables directly")
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Fallback API key if not found
    if not api_key:
        api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key  # Also set GOOGLE_API_KEY for compatibility
        print("⚠️  Using fallback API key")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not configured")
        print("   Please set your Gemini API key in the .env file")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    try:
        print("[DEBUG] Creating GenerativeModel")
        print(f"[DEBUG] API Key: {api_key[:10]}...")
        # Set the API key in environment and create model
        os.environ["GOOGLE_API_KEY"] = api_key
        # API key is set in environment
        
        model = GenerativeModel('gemini-1.5-flash')
        print("[DEBUG] Sending test prompt")
        # Test with a simple prompt
        response = model.generate_content("Hello! Can you confirm you're working? Just respond with 'Yes, I'm working!'")
        
        print("✅ Gemini AI is working!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Gemini AI: {e}")
        print("   Please check your API key and internet connection")
        return False

def test_medical_analysis():
    print("[DEBUG] test_medical_analysis called")
    """Test medical analysis capabilities"""
    
    try:
        from agents import GEMINI_AVAILABLE, doctor, verifier, nutritionist, exercise_specialist
        print("[DEBUG] Imported agents")
        if not GEMINI_AVAILABLE:
            print("❌ Gemini AI not available - check API key configuration")
            return False
        
        if not all([doctor, verifier, nutritionist, exercise_specialist]):
            print("❌ Not all medical agents are available")
            return False
        
        print("✅ All medical agents are properly configured!")
        print(f"   - Doctor: {doctor.role if doctor else 'Not available'}")
        print(f"   - Verifier: {verifier.role if verifier else 'Not available'}")
        print(f"   - Nutritionist: {nutritionist.role if nutritionist else 'Not available'}")
        print(f"   - Exercise Specialist: {exercise_specialist.role if exercise_specialist else 'Not available'}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing medical agents: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini AI Integration...")
    print("=" * 50)
    
    # Test basic connection
    connection_ok = test_gemini_connection()
    
    if connection_ok:
        print("\n" + "=" * 50)
        # Test medical agents
        agents_ok = test_medical_analysis()
        
        if agents_ok:
            print("\n🎉 All tests passed! Gemini AI is ready for blood test analysis.")
        else:
            print("\n⚠️  Basic connection works, but medical agents need configuration.")
    else:
        print("\n❌ Gemini AI connection failed. Please check your setup.")
    
    print("\n" + "=" * 50)
    print("📝 Next steps:")
    print("1. If tests passed: Start your application and test with a blood report")
    print("2. If tests failed: Check the setup guide in SETUP_API_KEY.md")
    print("3. Get help: Visit https://makersuite.google.com/app/apikey") 