import os
import sys
# Set dummy environment variables to avoid real API calls or errors
os.environ["GOOGLE_API_KEY"] = "dummy_key"
os.environ["TAVILY_API_KEY"] = "dummy_key"

try:
    print("Attempting to import agents...")
    from app.services.agents import RoadmapAgent, ResourcesAgent, QuizAgent, SummarizerAgent, MathSolverAgent, JobSearchAgent
    print("Imports successful!")
    
    # Instantiate agents
    print("Testing RoadmapAgent instantiation...")
    r = RoadmapAgent()
    print("RoadmapAgent OK")
    
    print("Testing ResourcesAgent instantiation...")
    res = ResourcesAgent()
    print("ResourcesAgent OK")
    
    print("Testing QuizAgent instantiation...")
    q = QuizAgent()
    print("QuizAgent OK")
    
    print("Testing SummarizerAgent instantiation...")
    s = SummarizerAgent()
    print("SummarizerAgent OK")
    
    print("Testing MathSolverAgent instantiation...")
    m = MathSolverAgent()
    print("MathSolverAgent OK")
    
    print("Testing JobSearchAgent instantiation...")
    j = JobSearchAgent()
    print("JobSearchAgent OK")
    
    print("ALL AGENTS INSTANTIATED SUCCESSFULLY!")
    
except ImportError as e:
    print(f"ImportError: {e}")
except NameError as e:
    print(f"NameError: {e}")
except Exception as e:
    print(f"Error: {e}")
