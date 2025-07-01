#!/usr/bin/env python3
"""
Minimal test for CrewAI with Gemini integration
"""

import os
from dotenv import load_dotenv

def test_minimal_crewai_gemini():
    """Test minimal CrewAI setup with Gemini"""
    print("Testing Minimal CrewAI with Gemini...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if required packages are available
    try:
        from crewai import Agent, Task, Crew
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("Required packages imported successfully")
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment")
        return False
    
    try:
        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        print("LLM created successfully")
        
        # Create simple agent
        agent = Agent(
            role="Medical Assistant",
            goal="Provide basic medical information",
            backstory="You are a helpful medical assistant who explains medical concepts in simple terms.",
            llm=llm,
            verbose=True
        )
        print("Agent created successfully")
        
        # Create simple task
        task = Task(
            description="Provide a brief explanation of what blood tests measure",
            agent=agent,
            expected_output="A concise explanation of what blood tests measure."
        )
        print("Task created successfully")
        
        # Create crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        print("Crew created successfully")
        
        print("Minimal CrewAI with Gemini test passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_minimal_crewai_gemini() 