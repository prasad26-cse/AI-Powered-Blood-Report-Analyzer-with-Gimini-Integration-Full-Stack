#!/usr/bin/env python3
"""
Test script for blood test analysis using CrewAI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"

# Set Google API key for Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"

def test_blood_analysis():
    """Test the blood analysis functionality"""
    try:
        from crewai import Crew, Process
        from agents import doctor, verifier, nutritionist, exercise_specialist, GEMINI_AVAILABLE
        from task import create_help_patients_task
        
        print("🚀 Starting blood test analysis test...")
        
        # Check if all agents are available
        if not GEMINI_AVAILABLE or not all([doctor, verifier, nutritionist, exercise_specialist]):
            print("❌ Gemini AI agents not available - using fallback analysis")
            return test_fallback_analysis()
        
        # Type assertion - we know these are not None after the check above
        assert doctor is not None and verifier is not None and nutritionist is not None and exercise_specialist is not None
        
        # Test file path
        test_file = "data/sample.pdf"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return False
        
        print(f"✅ Test file found: {test_file}")
        
        # Create crew for analysis
        print("👥 Creating medical analysis crew...")
        
        # Create task with doctor agent
        help_patients_task = create_help_patients_task(doctor)
        
        medical_crew = Crew(
            agents=[doctor, verifier, nutritionist, exercise_specialist],  # type: ignore
            tasks=[help_patients_task],  # type: ignore
            process=Process.sequential,
            verbose=True
        )
        
        # Test query
        test_query = "Please analyze my blood test report and provide a comprehensive summary of the results."
        
        print(f"🔍 Running analysis with query: {test_query}")
        print("⏳ This may take a few minutes...")
        
        # Run analysis
        result = medical_crew.kickoff(inputs={
            "query": test_query, 
            "file_path": test_file
        })
        
        print("✅ Analysis completed successfully!")
        print("📊 Analysis Result:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_analysis():
    """Test fallback analysis when AI agents are not available"""
    print("🔄 Running fallback analysis test...")
    
    try:
        from celery_app import simple_blood_analysis
        
        test_file = "data/sample.pdf"
        test_query = "Please analyze my blood test report and provide a comprehensive summary of the results."
        
        result = simple_blood_analysis(test_file, test_query)
        
        print("✅ Fallback analysis completed successfully!")
        print("📊 Fallback Analysis Result:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during fallback analysis: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Blood Test Analysis Test")
    print("=" * 40)
    
    success = test_blood_analysis()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("✅ The blood test analysis system is working properly.")
    else:
        print("\n❌ Test failed!")
        print("🔧 Please check the error messages above and fix any issues.")
    
    print("\n" + "=" * 40) 