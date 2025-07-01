#!/usr/bin/env python3
"""
Enhanced simple analysis using Gemini AI
"""

import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel
import PyPDF2

def enhanced_simple_blood_analysis(file_path: str, query: str) -> dict:
    """Enhanced simple analysis using Gemini AI"""
    try:
        # Use API key from environment
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No Gemini API key found in environment!")
            return {"status": "error", "result": "No Gemini API key found in environment!", "fallback": True}
        print(f"[Gemini] API key loaded: {api_key[:6]}...{api_key[-2:]}")
        # The latest SDK uses the environment variable, no need to set in code
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
