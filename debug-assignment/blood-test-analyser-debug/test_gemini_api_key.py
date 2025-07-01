import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    from google.generativeai.generative_models import GenerativeModel
except ImportError:
    print("google-generativeai package is not installed. Please install it with 'pip install google-generativeai'.")
    exit(1)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ No Gemini API key found in environment!")
    exit(1)
print(f"[Gemini] API key loaded: {api_key[:6]}...{api_key[-2:]}")

try:
    # The latest SDK uses the environment variable, no need to set in code
    model = GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello! Please respond with 'Gemini is working correctly!'")
    print("✅ Gemini 1.5 Flash API connection successful!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Gemini API test failed: {e}") 