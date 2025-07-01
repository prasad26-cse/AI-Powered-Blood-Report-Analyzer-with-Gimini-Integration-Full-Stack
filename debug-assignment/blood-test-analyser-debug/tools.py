## Importing libraries and environment
import os
from dotenv import load_dotenv
load_dotenv()

# Tools
# from langchain_community.tools import DuckDuckGoSearchRun, Tool
from langchain_community.tools import Tool
from langchain_community.document_loaders import PyPDFLoader
import PyPDF2
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Search Tool (Temporarily disabled to avoid import issues)
# search_tool = DuckDuckGoSearchRun()

# ✅ Blood Test PDF Reader Tool
class BloodTestReportTool:
    def __init__(self):
        pass

    @property
    def read_data_tool(self):
        """Returns a LangChain tool to read a PDF blood report"""

        def read_pdf(path='data/sample.pdf'):
            """
            Reads and cleans data from a PDF file with improved performance.

            Args:
                path (str): Path of the PDF file

            Returns:
                str: Cleaned text content from the file
            """
            try:
                # First try with PyPDF2 for better performance
                try:
                    with open(path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        full_report = ""
                        
                        for page_num, page in enumerate(pdf_reader.pages):
                            try:
                                content = page.extract_text()
                                if content:
                                    # Clean up extra line breaks and whitespace
                                    content = ' '.join(content.split())
                                    full_report += content.strip() + "\n"
                            except Exception as page_error:
                                logger.warning(f"Error extracting text from page {page_num}: {page_error}")
                                continue
                        
                        if full_report.strip():
                            return full_report.strip()
                except Exception as pypdf_error:
                    logger.warning(f"PyPDF2 failed, trying PyPDFLoader: {pypdf_error}")
                
                # Fallback to PyPDFLoader if PyPDF2 fails
                docs = PyPDFLoader(file_path=path).load()
                full_report = ""

                for data in docs:
                    content = data.page_content

                    # Clean up extra line breaks and whitespace
                    content = ' '.join(content.split())
                    full_report += content.strip() + "\n"

                return full_report.strip()

            except Exception as e:
                logger.error(f"Failed to read PDF file {path}: {str(e)}")
                return f"Failed to read PDF file: {str(e)}"

        return Tool(
            name="read_pdf",
            description="Reads and extracts text content from a PDF file with improved performance",
            func=read_pdf
        )

    def extract_text_fast(self, file_path: str) -> str:
        """
        Fast PDF text extraction using PyPDF2
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                for page in pdf_reader.pages:
                    try:
                        content = page.extract_text()
                        if content:
                            # Clean and normalize text
                            content = ' '.join(content.split())
                            text_parts.append(content)
                    except Exception as e:
                        logger.warning(f"Error extracting text from page: {e}")
                        continue
                
                return '\n'.join(text_parts)
        except Exception as e:
            logger.error(f"Fast PDF extraction failed: {e}")
            return ""

# ✅ Placeholder Nutrition Tool (Future Ready)
class NutritionTool:
    def __init__(self):
        pass

    @property
    def analyze_nutrition_tool(self):
        def analyze(blood_report_data):
            processed_data = blood_report_data.replace("  ", " ")
            # TODO: Add actual logic here
            return "Nutrition analysis functionality to be implemented"
        
        return Tool(
            name="analyze_nutrition",
            description="Analyzes blood report data for nutrition recommendations",
            func=analyze
        )


# ✅ Placeholder Exercise Tool (Future Ready)
class ExerciseTool:
    def __init__(self):
        pass

    @property
    def create_exercise_plan_tool(self):
        def plan(blood_report_data):
            # TODO: Add exercise planning logic here
            return "Exercise planning functionality to be implemented"
        
        return Tool(
            name="create_exercise_plan",
            description="Creates exercise plans based on blood report data",
            func=plan
        )
