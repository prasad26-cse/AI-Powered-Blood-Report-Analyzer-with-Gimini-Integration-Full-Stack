## Importing libraries and files
import os
from dotenv import load_dotenv
from crewai import Agent
from tools import BloodTestReportTool
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LLM_IMPORT_OK = True
except Exception as e:
    print(f"❌ Error importing ChatGoogleGenerativeAI: {e}")
    LLM_IMPORT_OK = False

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Use the correct API key if not set
if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyCfRw4jp65Dl-jiA95TOz6e0hauRLWJW4o":
    GEMINI_API_KEY = "AIzaSyCp1PLO5Sowk0ladBV_BF8E8k2iwwU2_HY"
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    print("✅ Using correct Gemini API key")

if not LLM_IMPORT_OK:
    print("⚠️  Warning: Gemini LLM import failed.")
    GEMINI_AVAILABLE = False
else:
    GEMINI_AVAILABLE = True
    # Set the environment variable for ChatGoogleGenerativeAI
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    print("✅ Gemini LLM configured successfully")

# ✅ Loading LLM using Gemini for CrewAI
if GEMINI_AVAILABLE:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=2048
        )
        print("✅ Gemini LLM configured successfully for CrewAI!")
    except Exception as e:
        print(f"❌ Error configuring Gemini LLM: {e}")
        GEMINI_AVAILABLE = False
        llm = None
else:
    llm = None
    print("⚠️  Using fallback analysis mode - no AI agents available (see logs above for reason)")

# ✅ Creating a Professional Medical Doctor agent
pdf_tool = BloodTestReportTool().read_data_tool

if GEMINI_AVAILABLE and llm:
    doctor = Agent(
        role="Senior Medical Doctor and Blood Test Specialist",
        goal="Analyze blood test reports professionally and provide accurate medical interpretations",
        verbose=True,
        backstory=(
            "You are a board-certified internal medicine physician with over 15 years of experience "
            "in interpreting blood test results. You have specialized training in hematology and "
            "laboratory medicine. You provide evidence-based analysis and clear explanations of "
            "blood test findings, always considering normal ranges, patient context, and potential "
            "clinical implications. You are thorough, accurate, and professional in your assessments."
        ),
        llm=llm,
        max_iter=3,
        max_rpm=10,
        allow_delegation=True
    )

    # ✅ Creating a Clinical Laboratory Scientist agent
    verifier = Agent(
        role="Clinical Laboratory Scientist and Quality Assurance Specialist",
        goal="Verify blood test report accuracy and ensure proper interpretation of laboratory values",
        verbose=True,
        backstory=(
            "You are a certified clinical laboratory scientist with expertise in hematology, "
            "chemistry, and immunology testing. You have extensive experience in quality control, "
            "method validation, and result interpretation. You ensure that blood test results are "
            "accurate, properly formatted, and within expected ranges. You can identify potential "
            "errors, artifacts, or unusual patterns that require attention."
        ),
        llm=llm,
        max_iter=2,
        max_rpm=8,
        allow_delegation=True
    )

    # ✅ Clinical Nutritionist agent
    nutritionist = Agent(
        role="Registered Dietitian and Clinical Nutritionist",
        goal="Provide evidence-based nutritional recommendations based on blood test results",
        verbose=True,
        backstory=(
            "You are a registered dietitian with a master's degree in clinical nutrition and "
            "certification in medical nutrition therapy. You have extensive experience working "
            "with patients with various medical conditions. You provide personalized nutrition "
            "recommendations based on blood test results, considering factors like glucose levels, "
            "lipid profiles, kidney function, liver enzymes, and micronutrient status. Your advice "
            "is always evidence-based and practical."
        ),
        llm=llm,
        max_iter=2,
        max_rpm=8,
        allow_delegation=False
    )

    # ✅ Exercise Physiologist agent
    exercise_specialist = Agent(
        role="Exercise Physiologist and Physical Activity Specialist",
        goal="Provide safe and appropriate exercise recommendations based on blood test results",
        verbose=True,
        backstory=(
            "You are a certified exercise physiologist with a master's degree in exercise science "
            "and specialized training in clinical exercise physiology. You have experience working "
            "with patients with various health conditions and understand how blood test results "
            "can impact exercise capacity and safety. You provide personalized exercise recommendations "
            "that consider cardiovascular health, muscle function, energy metabolism, and any "
            "medical contraindications identified in blood tests."
        ),
        llm=llm,
        max_iter=2,
        max_rpm=8,
        allow_delegation=False
    )
else:
    # Fallback agents when Gemini is not available
    class DummyAgent:
        def __init__(self, name):
            self.name = name
            self.role = name  # Add role attribute for compatibility
        def run(self, *args, **kwargs):
            return f"{self.name} agent is unavailable (no LLM configured)."
    doctor = DummyAgent("Doctor")
    verifier = DummyAgent("Verifier")
    nutritionist = DummyAgent("Nutritionist")
    exercise_specialist = DummyAgent("Exercise Specialist")
    print("⚠️  Using fallback analysis mode - no AI agents available")
