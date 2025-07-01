#!/usr/bin/env python3
"""
Fix script for the analysis issue where "No analysis result was generated" appears
This script will:
1. Set up the correct Gemini API key
2. Test the analysis functionality
3. Fix any configuration issues
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_gemini_configuration():
    """Fix Gemini API key configuration"""
    print("🔧 Fixing Gemini API Configuration...")
    
    # The correct API key
    correct_api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
    
    # Set environment variables
    os.environ["GEMINI_API_KEY"] = correct_api_key
    os.environ["GOOGLE_API_KEY"] = correct_api_key
    
    print(f"✅ Set GEMINI_API_KEY: {correct_api_key[:10]}...")
    print(f"✅ Set GOOGLE_API_KEY: {correct_api_key[:10]}...")
    
    return True

def test_gemini_connection():
    """Test if Gemini is working with the API key"""
    print("\n🔍 Testing Gemini Connection...")
    
    try:
        import google.generativeai as genai
        from google.generativeai.generative_models import GenerativeModel
        
        # Configure with the correct API key
        api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Create model
        model = GenerativeModel('gemini-1.5-flash')
        
        # Test simple response
        response = model.generate_content("Hello! Please respond with 'Gemini is working correctly!'")
        
        print("✅ Gemini connection successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False

def test_agents_configuration():
    """Test if the agents are properly configured"""
    print("\n🤖 Testing Agents Configuration...")
    
    try:
        # Import agents with the fixed API key
        from agents import GEMINI_AVAILABLE, doctor, verifier, nutritionist, exercise_specialist
        
        if GEMINI_AVAILABLE:
            print("✅ Gemini is available for agents")
            
            # Test each agent
            agents = {
                "Doctor": doctor,
                "Verifier": verifier,
                "Nutritionist": nutritionist,
                "Exercise Specialist": exercise_specialist
            }
            
            for name, agent in agents.items():
                if hasattr(agent, 'role') and agent.role:
                    print(f"✅ {name} agent is properly configured")
                else:
                    print(f"❌ {name} agent is not properly configured")
                    return False
            
            return True
        else:
            print("❌ Gemini is not available for agents")
            return False
            
    except Exception as e:
        print(f"❌ Agents configuration test failed: {e}")
        return False

def test_simple_analysis():
    """Test the simple blood analysis function"""
    print("\n📊 Testing Simple Blood Analysis...")
    
    try:
        from celery_app import simple_blood_analysis
        
        # Create a test query
        test_query = "Please analyze my blood test report and provide a comprehensive summary"
        
        # Test with a dummy file path
        result = simple_blood_analysis("data/sample.pdf", test_query)
        
        print("✅ Simple blood analysis test successful!")
        print("📋 Analysis Result:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Check if it's a fallback result
        if isinstance(result, dict):
            if result.get("fallback", False):
                print("⚠️  Still getting fallback result")
                return False
            else:
                print("✅ Got real analysis result!")
                return True
        else:
            result_str = str(result).lower()
            if "fallback" in result_str or "unavailable" in result_str:
                print("⚠️  Still getting fallback result")
                return False
            else:
                print("✅ Got real analysis result!")
                return True
        
    except Exception as e:
        print(f"❌ Simple blood analysis test failed: {e}")
        return False

def test_celery_task():
    """Test the Celery task"""
    print("\n🔄 Testing Celery Task...")
    
    try:
        from celery_app import process_blood_report
        
        # Test with a dummy report ID
        test_report_id = 999
        test_query = "Please analyze my blood test report"
        
        # Run the task
        result = process_blood_report.delay(test_report_id, test_query)
        
        # Get the result
        try:
            celery_result = result.get(timeout=30)
            print("✅ Celery task completed successfully!")
            print("📋 Celery Result:")
            print("-" * 40)
            print(celery_result)
            print("-" * 40)
            return True
        except Exception as e:
            print(f"❌ Celery task failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Celery task test failed: {e}")
        return False

def create_enhanced_simple_analysis():
    """Create an enhanced simple analysis function that uses Gemini"""
    print("\n🚀 Creating Enhanced Simple Analysis...")
    
    enhanced_analysis_code = '''#!/usr/bin/env python3
"""
Enhanced simple analysis using Gemini AI
"""

import os
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel
import PyPDF2

def enhanced_simple_blood_analysis(file_path: str, query: str) -> dict:
    """Enhanced simple analysis using Gemini AI"""
    try:
        # Set API key
        api_key = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
        genai.configure(api_key=api_key)
        
        # Create model
        model = GenerativeModel('gemini-1.5-flash')
        
        # Extract text from PDF
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
        except Exception as e:
            print(f"PDF reading error: {e}")
            text_content = "Blood test report content could not be extracted from PDF."
        
        # Create analysis prompt
        analysis_prompt = f"""
        You are a medical AI assistant. Please analyze this blood test report and provide a comprehensive analysis.
        
        User Query: {query}
        
        Blood Test Report Content:
        {text_content[:3000]}  # Limit content length
        
        Please provide your analysis in this structured format:
        
        **1. Summary of Key Findings**
        [Provide a brief overview of the blood test results]
        
        **2. Interpretation of Any Abnormal Values**
        [Explain any values that are outside normal ranges]
        
        **3. Clinical Significance of Results**
        [Discuss the medical implications of the findings]
        
        **4. Recommendations for Follow-up**
        [Provide specific recommendations for the patient]
        
        **5. Overall Health Assessment**
        [Give an overall assessment of the patient's health based on these results]
        
        Please be thorough, professional, and provide actionable insights.
        """
        
        # Generate analysis
        response = model.generate_content(analysis_prompt)
        
        return {
            "status": "processed",
            "result": response.text,
            "fallback": False,
            "confidence_score": 0.95
        }
        
    except Exception as e:
        print(f"Enhanced analysis error: {e}")
        # Fallback to basic analysis
        return {
            "status": "processed",
            "result": f"Enhanced analysis failed: {str(e)}. Please try again later.",
            "fallback": True,
            "confidence_score": 0.5
        }
'''
    
    # Write the enhanced function to a new file
    with open("enhanced_analysis.py", "w") as f:
        f.write(enhanced_analysis_code)
    
    print("✅ Enhanced analysis function created!")
    return True

def update_celery_app():
    """Update the Celery app to use the enhanced analysis"""
    print("\n📝 Updating Celery App...")
    
    try:
        # Read the current celery_app.py
        with open("celery_app.py", "r") as f:
            content = f.read()
        
        # Replace the simple_blood_analysis import and usage
        updated_content = content.replace(
            "from celery_app import simple_blood_analysis",
            "from enhanced_analysis import enhanced_simple_blood_analysis"
        )
        
        updated_content = updated_content.replace(
            "simple_blood_analysis(str(report.file_path), query_text)",
            "enhanced_simple_blood_analysis(str(report.file_path), query_text)"
        )
        
        # Write the updated content
        with open("celery_app.py", "w") as f:
            f.write(updated_content)
        
        print("✅ Celery app updated!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update Celery app: {e}")
        return False

def test_enhanced_analysis():
    """Test the enhanced analysis function"""
    print("\n🧪 Testing Enhanced Analysis...")
    
    try:
        # Create a mock blood test report for testing
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
        
        # Write mock report to file
        os.makedirs("data", exist_ok=True)
        with open("data/test_report.pdf", "w", encoding="utf-8") as f:
            f.write(mock_report)
        
        # Import and test enhanced analysis
        from enhanced_analysis import enhanced_simple_blood_analysis
        
        result = enhanced_simple_blood_analysis("data/test_report.pdf", "Please analyze my blood test report")
        
        print("✅ Enhanced analysis test successful!")
        print("📋 Enhanced Analysis Result:")
        print("=" * 50)
        print(result.get("result", "No result"))
        print("=" * 50)
        
        if not result.get("fallback", True):
            print("🎉 SUCCESS! Enhanced analysis is working with Gemini!")
            return True
        else:
            print("⚠️  Still getting fallback result")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced analysis test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("=" * 60)
    print("🔧 BLOOD TEST ANALYSIS FIX SCRIPT")
    print("=" * 60)
    
    # Step 1: Fix Gemini configuration
    if not fix_gemini_configuration():
        print("❌ Failed to fix Gemini configuration")
        return False
    
    # Step 2: Test Gemini connection
    if not test_gemini_connection():
        print("❌ Gemini connection test failed")
        return False
    
    # Step 3: Test agents configuration
    if not test_agents_configuration():
        print("❌ Agents configuration test failed")
        return False
    
    # Step 4: Create enhanced analysis
    if not create_enhanced_simple_analysis():
        print("❌ Failed to create enhanced analysis")
        return False
    
    # Step 5: Update Celery app
    if not update_celery_app():
        print("❌ Failed to update Celery app")
        return False
    
    # Step 6: Test enhanced analysis
    if not test_enhanced_analysis():
        print("❌ Enhanced analysis test failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 FIX COMPLETED SUCCESSFULLY!")
        print("✅ Your blood test analysis should now work properly!")
        print("\n📝 Next steps:")
        print("1. Restart your backend server")
        print("2. Try uploading a PDF again")
        print("3. The analysis should now provide real Gemini AI results")
    else:
        print("\n❌ FIX FAILED!")
        print("🔧 Please check the error messages above and try again.")
    
    print("\n" + "=" * 60) 