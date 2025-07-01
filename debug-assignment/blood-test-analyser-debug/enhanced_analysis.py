#!/usr/bin/env python3
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
