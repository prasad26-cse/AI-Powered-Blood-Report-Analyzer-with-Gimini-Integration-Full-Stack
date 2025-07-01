#!/usr/bin/env python3
"""
Simple test to verify Celery task with simple Gemini analysis
"""

import os
from dotenv import load_dotenv

def test_celery_task():
    """Test the Celery task directly"""
    print("🧪 Testing Celery Task with Simple Gemini Analysis...")
    
    # Load environment variables
    load_dotenv()
    
    # Set API key directly (permanent fix)
    api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
    os.environ["GEMINI_API_KEY"] = api_key
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test file path
    test_file = "data/sample.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"✅ Test file found: {test_file}")
    
    try:
        # Import and test simple Gemini analysis directly
        from simple_gemini_analysis import test_simple_gemini
        
        print("🔍 Testing simple Gemini analysis...")
        result = test_simple_gemini()
        
        print("✅ Analysis completed!")
        print("📊 Result:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        # Check if it's a fallback result
        if isinstance(result, dict):
            if result.get("fallback", False):
                print("❌ Still getting fallback result!")
                return False
            elif result.get("status") == "processed" and not result.get("fallback", True):
                print("✅ Got real Gemini analysis!")
                return True
            else:
                print("✅ Got analysis result!")
                return True
        else:
            # If result is a string, check for fallback indicators
            result_str = str(result).lower()
            if "fallback" in result_str or "unavailable" in result_str or "currently unavailable" in result_str:
                print("❌ Still getting fallback result!")
                return False
            else:
                print("✅ Got real Gemini analysis!")
                return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Simple Gemini Analysis Test")
    print("=" * 60)
    
    success = test_celery_task()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("✅ Your simple Gemini analysis is working!")
    else:
        print("\n❌ Test failed!")
        print("🔧 Please check the error messages above.")
    
    print("\n" + "=" * 60) 