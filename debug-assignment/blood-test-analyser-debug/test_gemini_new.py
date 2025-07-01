#!/usr/bin/env python3
"""
Test script for Gemini AI integration using environment API key.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def test_gemini_basic():
    """Test basic Gemini AI connection and functionality"""
    print("🔍 Testing Basic Gemini AI Connection...")
    try:
        import google.generativeai as genai
        from google.generativeai.generative_models import GenerativeModel

        api_key = get_gemini_api_key()
        if not api_key:
            print("❌ No Gemini API key found in environment!")
            return False
        print(f"[Gemini] API key loaded: {api_key[:6]}...{api_key[-2:]}")
        # The latest SDK uses the environment variable, no need to set in code

        model = GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello! Please respond with 'Gemini is working correctly!'")
        print("✅ Basic Gemini connection successful!")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Basic Gemini test failed: {e}")
        return False

def test_gemini_medical_knowledge():
    """Test Gemini's medical knowledge and analysis capabilities"""
    print("\n🏥 Testing Medical Knowledge...")
    
    try:
        import google.generativeai as genai
        from google.generativeai.generative_models import GenerativeModel
        
        # Set API key
        api_key = get_gemini_api_key()
        if not api_key:
            print("❌ No Gemini API key found in environment!")
            return False
        print(f"[Gemini] API key loaded: {api_key[:6]}...{api_key[-2:]}")
        
        # Create model
        model = GenerativeModel('gemini-1.5-flash')
        
        # Test medical knowledge
        medical_prompt = """
        You are a medical AI assistant. Please provide a brief explanation of:
        1. What is a Complete Blood Count (CBC)?
        2. What are normal ranges for hemoglobin in adults?
        3. What does high white blood cell count typically indicate?
        
        Keep your response concise and professional.
        """
        
        response = model.generate_content(medical_prompt)
        
        print("✅ Medical knowledge test successful!")
        print("📋 Medical Response:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        return True
        
    except Exception as e:
        print(f"❌ Medical knowledge test failed: {e}")
        return False

def test_gemini_pdf_analysis():
    """Test Gemini's ability to analyze PDF content"""
    print("\n📄 Testing PDF Analysis Capabilities...")
    
    try:
        import google.generativeai as genai
        from google.generativeai.generative_models import GenerativeModel
        import PyPDF2
        
        # Set API key
        api_key = get_gemini_api_key()
        if not api_key:
            print("❌ No Gemini API key found in environment!")
            return False
        print(f"[Gemini] API key loaded: {api_key[:6]}...{api_key[-2:]}")
        
        # Create model
        model = GenerativeModel('gemini-1.5-flash')
        
        # Check if sample PDF exists
        sample_pdf = "data/sample.pdf"
        if not os.path.exists(sample_pdf):
            print(f"⚠️  Sample PDF not found: {sample_pdf}")
            print("   Creating a mock blood test report for testing...")
            
            # Create mock blood test data
            mock_report = """
            BLOOD TEST REPORT
            
            Patient: John Doe
            Date: 2024-01-15
            
            Complete Blood Count (CBC):
            - Hemoglobin: 14.2 g/dL (Normal: 13.5-17.5)
            - White Blood Cells: 7,500/μL (Normal: 4,500-11,000)
            - Red Blood Cells: 4.8 M/μL (Normal: 4.5-5.9)
            - Platelets: 250,000/μL (Normal: 150,000-450,000)
            
            Comprehensive Metabolic Panel:
            - Glucose: 95 mg/dL (Normal: 70-100)
            - Creatinine: 0.9 mg/dL (Normal: 0.7-1.3)
            - BUN: 15 mg/dL (Normal: 7-20)
            
            Lipid Panel:
            - Total Cholesterol: 180 mg/dL (Normal: <200)
            - HDL: 55 mg/dL (Normal: >40)
            - LDL: 100 mg/dL (Normal: <100)
            - Triglycerides: 120 mg/dL (Normal: <150)
            """
            
            # Test with mock data
            analysis_prompt = f"""
            Analyze this blood test report and provide:
            1. Overall health assessment
            2. Any abnormal values
            3. Recommendations for follow-up
            
            Report:
            {mock_report}
            """
            
            response = model.generate_content(analysis_prompt)
            
            print("✅ PDF analysis test successful (using mock data)!")
            print("📊 Analysis Result:")
            print("=" * 50)
            print(response.text)
            print("=" * 50)
            return True
            
        else:
            # Read actual PDF
            with open(sample_pdf, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            
            # Test with actual PDF content
            analysis_prompt = f"""
            Analyze this blood test report and provide:
            1. Overall health assessment
            2. Any abnormal values
            3. Recommendations for follow-up
            
            Report content:
            {text_content[:2000]}  # Limit content length
            """
            
            response = model.generate_content(analysis_prompt)
            
            print("✅ PDF analysis test successful!")
            print("📊 Analysis Result:")
            print("=" * 50)
            print(response.text)
            print("=" * 50)
            return True
        
    except Exception as e:
        print(f"❌ PDF analysis test failed: {e}")
        return False

def test_gemini_structured_analysis():
    """Test Gemini's ability to provide structured medical analysis"""
    print("\n🔬 Testing Structured Medical Analysis...")
    
    try:
        import google.generativeai as genai
        from google.generativeai.generative_models import GenerativeModel
        
        # Set API key
        api_key = get_gemini_api_key()
        if not api_key:
            print("❌ No Gemini API key found in environment!")
            return False
        print(f"[Gemini] API key loaded: {api_key[:6]}...{api_key[-2:]}")
        
        # Create model
        model = GenerativeModel('gemini-1.5-flash')
        
        # Test structured analysis
        structured_prompt = """
        Analyze the following blood test results and provide a structured response:
        
        Test Results:
        - Hemoglobin: 12.5 g/dL (Normal: 13.5-17.5)
        - White Blood Cells: 12,000/μL (Normal: 4,500-11,000)
        - Glucose: 110 mg/dL (Normal: 70-100)
        - Cholesterol: 220 mg/dL (Normal: <200)
        
        Please provide your analysis in this format:
        
        SUMMARY:
        [Brief overall assessment]
        
        ABNORMAL VALUES:
        [List and explain any abnormal values]
        
        POTENTIAL CONCERNS:
        [List potential health concerns]
        
        RECOMMENDATIONS:
        [List specific recommendations]
        
        SEVERITY:
        [Low/Medium/High risk assessment]
        """
        
        response = model.generate_content(structured_prompt)
        
        print("✅ Structured analysis test successful!")
        print("📋 Structured Analysis:")
        print("=" * 50)
        print(response.text)
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Structured analysis test failed: {e}")
        return False

def test_gemini_integration():
    """Test integration with the existing application components"""
    print("\n🔗 Testing Application Integration...")
    
    try:
        # Test if required modules can be imported
        from agents import GEMINI_AVAILABLE, doctor, verifier, nutritionist, exercise_specialist
        
        if GEMINI_AVAILABLE:
            print("✅ Gemini integration is available")
            
            # Test each agent
            agents = {
                "Doctor": doctor,
                "Verifier": verifier,
                "Nutritionist": nutritionist,
                "Exercise Specialist": exercise_specialist
            }
            
            for name, agent in agents.items():
                if agent:
                    print(f"✅ {name} agent is configured")
                else:
                    print(f"⚠️  {name} agent is not configured")
            
            return True
        else:
            print("❌ Gemini integration is not available")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all Gemini tests"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE GEMINI AI TEST SUITE")
    print("=" * 60)
    print("API Key: GEMINI_API_KEY or GOOGLE_API_KEY")
    print("=" * 60)
    
    tests = [
        ("Basic Connection", test_gemini_basic),
        ("Medical Knowledge", test_gemini_medical_knowledge),
        ("PDF Analysis", test_gemini_pdf_analysis),
        ("Structured Analysis", test_gemini_structured_analysis),
        ("Application Integration", test_gemini_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Gemini AI is ready for production use.")
    elif passed >= total * 0.8:
        print("\n⚠️  Most tests passed. Minor issues detected.")
    else:
        print("\n❌ Multiple tests failed. Please check your setup.")
    
    print("\n" + "=" * 60)
    print("📝 Next Steps:")
    print("1. If all tests passed: Your Gemini AI is ready!")
    print("2. If some tests failed: Check the error messages above")
    print("3. For help: Check SETUP_API_KEY.md or the documentation")
    print("=" * 60)

if __name__ == "__main__":
    main() 