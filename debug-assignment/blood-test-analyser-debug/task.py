from crewai import Task

def create_help_patients_task(doctor_agent):
    """Create the help patients task with the doctor agent"""
    return Task(
        description="Help patients understand their blood test reports and provide actionable advice.",
        agent=doctor_agent,
        expected_output="A clear, actionable summary and recommendations based on the blood test report."
    ) 