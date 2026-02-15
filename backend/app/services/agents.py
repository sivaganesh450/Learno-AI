"""
LangGraph-based AI Agents for LearnO using Local Llama via Ollama
Three specialized agents: Roadmap Generator, Resources Provider, Summarizer
"""

from typing import TypedDict, Annotated, List, Optional, Dict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_ollama import ChatOllama # Removed Ollama
import operator
import os
import httpx
import io
from dotenv import load_dotenv
from tavily import TavilyClient
from PIL import Image
from google import genai

load_dotenv()

# Initialize Tavily client for resource searching and job search
TAVILY_API_KEY = "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"
try:
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    print("Successfully initialized Tavily client")
except Exception as e:
    print(f"Warning: Could not initialize Tavily client: {e}")
    tavily_client = None

# Initialize Google GenAI Client
try:
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    print("Successfully initialized Google GenAI client")
except Exception as e:
    print(f"Warning: Could not initialize Google GenAI client: {e}")
    client = None


# State definitions for each agent
class RoadmapState(TypedDict):
    messages: Annotated[List, operator.add]
    topic: str
    skill_level: str
    duration: str
    skills_known: Optional[str]
    roadmap: Optional[str]


class ResourcesState(TypedDict):
    messages: Annotated[List, operator.add]
    topic: str
    skill_level: str
    resource_type: str
    resources: Optional[str]


class QAState(TypedDict):
    messages: Annotated[List, operator.add]
    question: str
    context: Optional[str]
    answer: Optional[str]


class QuizState(TypedDict):
    """State for Quiz/Q&A Agent"""
    messages: Annotated[List, operator.add]
    domain: str
    purpose: str  # interview, exam, knowledge_test
    difficulty: str  # easy, moderate, difficult
    current_question: Optional[str]
    user_answer: Optional[str]
    rating: Optional[int]  # 1-5 scale
    feedback: Optional[str]
    score: int
    questions_asked: int
    session_active: bool


class MathProblemState(TypedDict):
    """State for Math Problem Solver Agent"""
    messages: Annotated[List, operator.add]
    problem: str
    problem_type: Optional[str]  # algebra, calculus, geometry, etc.
    steps: Optional[List[str]]
    final_answer: Optional[str]
    explanation: Optional[str]


class JobSearchState(TypedDict):
    """State for Job Search Agent"""
    messages: Annotated[List, operator.add]
    query: str
    location: Optional[str]
    country: str  # gb, us, au, etc.
    page: int
    results_per_page: int
    jobs: Optional[List[Dict]]


class RoadmapAgent:
    """Agent for generating personalized learning roadmaps using Gemini"""
    
    def __init__(self):
        self.name = "Roadmap Generator"
        self.client = client
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(RoadmapState)
        
        # Add nodes
        workflow.add_node("generate_roadmap", self._generate_roadmap)
        
        # Add edges
        workflow.set_entry_point("generate_roadmap")
        workflow.add_edge("generate_roadmap", END)
        
        return workflow.compile()
    
    def _generate_roadmap(self, state: RoadmapState) -> dict:
        """Generate the learning roadmap using Gemini"""
        topic = state["topic"]
        skill_level = state["skill_level"]
        duration = state["duration"]
        skills_known = state.get("skills_known", "")
        
        # If Client is not available, use fallback
        if not self.client:
            print("Gemini client not available, using fallback")
            return self._fallback_roadmap(topic, skill_level, duration, skills_known)
        
        system_prompt = """You are an expert learning path designer. Create detailed, structured learning roadmaps.

CRITICAL: You MUST structure the roadmap according to the exact duration provided by the user.
- If the user says "1 month", create a 4-week roadmap
- If the user says "3 months", create a 12-week roadmap
- If the user says "6 months", create a 24-week roadmap
- Divide the total duration into logical phases (e.g., Foundation, Intermediate, Advanced)

Your response should include:
- Clear week-by-week or phase breakdown that FITS the specified duration
- Specific topics to learn each week/phase
- Recommended resources (courses, books, tutorials)
- Practical projects at each phase
- Milestones and checkpoints

Use emojis and markdown formatting. Make it comprehensive and actionable."""
        
        skills_info = f" They already know: {skills_known}." if skills_known else ""
        
        user_prompt = f"""Create a complete learning roadmap for {topic}.

**IMPORTANT - Duration: {duration}** - Structure the ENTIRE roadmap to fit within this timeframe.

Student Details:
- Current Level: {skill_level}
- Prior Knowledge: {skills_info if skills_info else 'None'}

Provide a week-by-week or phase-by-phase breakdown that fits within {duration}. Include specific topics, resources, projects, and milestones for each phase."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            print(f"Calling Gemini API for roadmap: {topic}")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            # Validate response
            if response and response.text:
                content = response.text.strip()
                
                # Check if response is valid (not just echoing the prompt)
                if len(content) > 100 and ("Phase" in content or "Week" in content or "#" in content):
                    print("Successfully generated roadmap from Gemini")
                    return {
                        "messages": [AIMessage(content=content)],
                        "roadmap": content
                    }
                else:
                    print(f"Invalid response from Gemini, using fallback. Response length: {len(content)}")
                    return self._fallback_roadmap(topic, skill_level, duration, skills_known)
            else:
                print("Empty response from Gemini, using fallback")
                return self._fallback_roadmap(topic, skill_level, duration, skills_known)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_roadmap(topic, skill_level, duration, skills_known)
    
    def _fallback_roadmap(self, topic: str, skill_level: str, duration: str, skills_known: str) -> dict:
        """Generate a detailed fallback roadmap when API is unavailable"""
        
        # Parse duration to get weeks
        duration_weeks = 12  # default
        if "month" in duration.lower():
            try:
                months = int(''.join(filter(str.isdigit, duration)))
                duration_weeks = months * 4
            except:
                pass
        elif "week" in duration.lower():
            try:
                duration_weeks = int(''.join(filter(str.isdigit, duration)))
            except:
                pass
        
        # Calculate phase durations
        phase1_end = max(2, duration_weeks // 6)
        phase2_end = max(phase1_end + 2, duration_weeks // 2)
        phase3_end = duration_weeks
        
        # Topic-specific content suggestions
        topic_lower = topic.lower()
        
        # Determine topic category and provide specific suggestions
        if any(x in topic_lower for x in ['python', 'java', 'javascript', 'c++', 'programming', 'coding']):
            foundation_topics = [
                f"Variables, data types, and operators in {topic}",
                f"Control flow: conditionals and loops",
                f"Functions and code organization",
                f"Basic data structures (lists, arrays, dictionaries)"
            ]
            intermediate_topics = [
                "Object-Oriented Programming (OOP) concepts",
                "Error handling and debugging",
                "File I/O and working with external data",
                "Working with libraries and packages"
            ]
            advanced_topics = [
                "Design patterns and best practices",
                "Testing and test-driven development",
                "Performance optimization",
                "Building real-world applications"
            ]
            projects = ["Calculator app", "To-do list application", "API integration project", "Full-stack application"]
            resources = ["Official documentation", "Codecademy", "freeCodeCamp", "LeetCode for practice"]
            
        elif any(x in topic_lower for x in ['web', 'html', 'css', 'react', 'angular', 'vue', 'frontend']):
            foundation_topics = [
                "HTML5 structure and semantic elements",
                "CSS fundamentals and layouts (Flexbox, Grid)",
                "Responsive design principles",
                "Basic JavaScript for interactivity"
            ]
            intermediate_topics = [
                f"Deep dive into {topic} framework/library",
                "Component-based architecture",
                "State management",
                "API integration and data fetching"
            ]
            advanced_topics = [
                "Performance optimization",
                "Testing React/Vue/Angular components",
                "Server-side rendering",
                "Deployment and CI/CD"
            ]
            projects = ["Personal portfolio", "Weather app", "E-commerce UI", "Full-featured web application"]
            resources = ["MDN Web Docs", "Frontend Masters", "CSS-Tricks", "React/Vue/Angular docs"]
            
        elif any(x in topic_lower for x in ['data', 'machine learning', 'ml', 'ai', 'deep learning', 'analytics']):
            foundation_topics = [
                "Python for data science (NumPy, Pandas)",
                "Data cleaning and preprocessing",
                "Exploratory Data Analysis (EDA)",
                "Statistics fundamentals"
            ]
            intermediate_topics = [
                "Machine learning algorithms (supervised/unsupervised)",
                "Feature engineering",
                "Model evaluation and validation",
                "Scikit-learn library"
            ]
            advanced_topics = [
                "Deep learning with TensorFlow/PyTorch",
                "Neural network architectures",
                "Model deployment",
                "MLOps and production systems"
            ]
            projects = ["Data analysis project", "Prediction model", "Classification system", "End-to-end ML pipeline"]
            resources = ["Kaggle", "Coursera ML courses", "Fast.ai", "Google ML Crash Course"]
            
        elif any(x in topic_lower for x in ['mobile', 'android', 'ios', 'flutter', 'react native', 'app']):
            foundation_topics = [
                f"Setting up {topic} development environment",
                "UI components and layouts",
                "Navigation between screens",
                "Handling user input"
            ]
            intermediate_topics = [
                "State management",
                "API integration",
                "Local storage and databases",
                "Push notifications"
            ]
            advanced_topics = [
                "Performance optimization",
                "Native module integration",
                "App store deployment",
                "Analytics and monitoring"
            ]
            projects = ["Notes app", "Weather app", "Social media clone", "Full-featured mobile app"]
            resources = ["Official docs", "Udemy courses", "YouTube tutorials", "Dev community forums"]
            
        else:
            # Generic but still useful
            foundation_topics = [
                f"Introduction to {topic} - core concepts",
                f"Setting up your {topic} environment",
                f"Basic terminology and fundamentals",
                f"Your first {topic} project"
            ]
            intermediate_topics = [
                f"Intermediate {topic} concepts",
                f"Best practices in {topic}",
                f"Common patterns and techniques",
                f"Working with real-world examples"
            ]
            advanced_topics = [
                f"Advanced {topic} techniques",
                f"Performance and optimization",
                f"Industry applications",
                f"Contributing to the community"
            ]
            projects = ["Starter project", "Intermediate project", "Portfolio project", "Real-world application"]
            resources = ["Official documentation", "Online courses", "YouTube tutorials", "Community forums"]
        
        # Build skills exclusion note
        skills_note = ""
        if skills_known:
            skills_note = f"\n\n> 💡 **Note:** Since you already know {skills_known}, feel free to skip familiar topics and focus on new concepts."
        
        roadmap = f"""# 🗺️ Learning Roadmap: {topic}

## 📋 Your Learning Profile
| Attribute | Value |
|-----------|-------|
| **Topic** | {topic} |
| **Current Level** | {skill_level.capitalize()} |
| **Duration** | {duration} ({duration_weeks} weeks) |
| **Known Skills** | {skills_known if skills_known else 'Starting fresh'} |
{skills_note}

---

## 🚀 Phase 1: Foundation (Week 1-{phase1_end})

### 📚 Topics to Master
{"".join([f"- ✅ {t}" + chr(10) for t in foundation_topics])}

### 🎯 Learning Goals
- Understand the fundamentals of {topic}
- Set up your development environment
- Complete basic exercises and tutorials
- Build confidence with core concepts

### 📖 Recommended Resources
- 📚 {resources[0]}
- 🎥 YouTube: "{topic} tutorial for beginners"
- 📝 Interactive platforms: {resources[1]}

### 💻 Project: {projects[0]}
Build a simple project to apply what you've learned.

---

## 📈 Phase 2: Skill Building (Week {phase1_end + 1}-{phase2_end})

### 📚 Topics to Master
{"".join([f"- ✅ {t}" + chr(10) for t in intermediate_topics])}

### 🎯 Learning Goals
- Deepen your understanding of {topic}
- Work on more complex problems
- Learn industry best practices
- Build a portfolio-worthy project

### 📖 Recommended Resources
- 🎓 Online courses: {resources[2]}
- 📚 Documentation and guides
- 👥 Join {topic} communities

### 💻 Projects
1. **{projects[1]}** - Apply intermediate concepts
2. **{projects[2]}** - Challenge yourself

---

## 🎯 Phase 3: Advanced & Mastery (Week {phase2_end + 1}-{phase3_end})

### 📚 Topics to Master
{"".join([f"- ✅ {t}" + chr(10) for t in advanced_topics])}

### 🎯 Learning Goals
- Master advanced concepts
- Build production-ready projects
- Contribute to open source
- Prepare for job opportunities

### 📖 Recommended Resources
- 📚 Advanced documentation
- 🎥 Conference talks and workshops
- 💼 Real-world case studies

### 💻 Capstone Project: {projects[3]}
Build a comprehensive project that showcases all your skills.

---

## ✅ Tips for Success

1. **Practice Daily** - Consistency beats intensity
2. **Build Projects** - Apply what you learn immediately
3. **Join Communities** - Learn from others and get help
4. **Document Your Journey** - Keep notes and share your progress
5. **Don't Give Up** - Challenges are part of learning!

---

## 🏆 Milestones & Checkpoints

| Week | Milestone | Status |
|------|-----------|--------|
| {phase1_end} | Complete Phase 1 - Foundation | ⬜ |
| {phase1_end + 2} | First project completed | ⬜ |
| {phase2_end} | Complete Phase 2 - Intermediate | ⬜ |
| {phase3_end} | Complete Phase 3 - Advanced | ⬜ |
| {phase3_end} | Portfolio project ready | ⬜ |

---

## 📚 Quick Resource Links

- 🔗 **Documentation**: Search "{topic} official documentation"
- 🎥 **Videos**: YouTube "{topic} complete course"
- 💬 **Community**: Reddit r/{topic.lower().replace(' ', '')} or Discord
- 📝 **Practice**: {resources[3]}

---

*This roadmap was generated based on your learning profile. The AI service is currently busy - for a more personalized roadmap with specific course links and tailored advice, please try again later!*
"""
        return {
            "messages": [AIMessage(content=roadmap)],
            "roadmap": roadmap
        }
    
    async def generate(self, message: str, topic: str, skill_level: str, duration: str, skills_known: str = "") -> str:
        """Generate a roadmap based on user input"""
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "topic": topic,
            "skill_level": skill_level,
            "duration": duration,
            "skills_known": skills_known,
            "roadmap": None
        }
        
        result = self.graph.invoke(initial_state)
        return result["roadmap"]
    
    async def generate_stream(self, message: str, topic: str, skill_level: str, duration: str, skills_known: str = ""):
        """Generate a roadmap with streaming response"""
        if not self.client:
            # Fallback - yield the whole response at once
            result = await self.generate(message, topic, skill_level, duration, skills_known)
            yield result
            return
        
        system_prompt = """You are an expert learning path designer. Create detailed, structured learning roadmaps.

CRITICAL: You MUST structure the roadmap according to the exact duration provided by the user.
- If the user says "1 month", create a 4-week roadmap
- If the user says "3 months", create a 12-week roadmap
- If the user says "6 months", create a 24-week roadmap
- Divide the total duration into logical phases (e.g., Foundation, Intermediate, Advanced)

Your response should include:
- Clear week-by-week or phase breakdown that FITS the specified duration
- Specific topics to learn each week/phase
- Recommended resources (courses, books, tutorials)
- Practical projects at each phase
- Milestones and checkpoints

Use emojis and markdown formatting. Make it comprehensive and actionable."""
        
        skills_info = f" They already know: {skills_known}." if skills_known else ""
        user_prompt = f"""Create a complete learning roadmap for {topic}.

**IMPORTANT - Duration: {duration}** - Structure the ENTIRE roadmap to fit within this timeframe.

Student Details:
- Current Level: {skill_level}
- Prior Knowledge: {skills_info if skills_info else 'None'}

Provide a week-by-week or phase-by-phase breakdown that fits within {duration}. Include specific topics, resources, projects, and milestones for each phase."""
        
        try:
            response = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"Streaming error: {e}")
            # Fallback to non-streaming
            result = await self.generate(message, topic, skill_level, duration, skills_known)
            yield result


class ResourcesAgent:
    """Agent for providing curated learning resources using LLM and Tavily search"""
    
    def __init__(self):
        self.name = "Resources Provider"
        self.client = client
        self.tavily = tavily_client
        self.graph = self._build_graph()
        # Store ChatMessageHistory per session (like the notebook pattern)
        self.session_histories: Dict[str, ChatMessageHistory] = {}
        self.k = 3  # Keep last k conversation turns (like ConversationBufferWindowMemory k parameter)
    
    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        """Get or create ChatMessageHistory for a session"""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = ChatMessageHistory()
        return self.session_histories[session_id]
    
    def get_windowed_history(self, session_id: str) -> List:
        """Get last k conversation turns (mimics ConversationBufferWindowMemory behavior)"""
        history = self.get_session_history(session_id)
        messages = history.messages
        # k conversations = k*2 messages (human + AI pairs)
        return messages[-(self.k * 2):] if len(messages) > self.k * 2 else messages
    
    def save_context(self, session_id: str, user_input: str, ai_output: str):
        """Save conversation context (like memory.save_context)"""
        history = self.get_session_history(session_id)
        history.add_user_message(user_input)
        history.add_ai_message(ai_output)
        print(f"[Memory] Saved context for session {session_id}. Total messages: {len(history.messages)}")
    
    def clear_session_history(self, session_id: str):
        """Clear history for a session"""
        if session_id in self.session_histories:
            del self.session_histories[session_id]
    
    def _search_tavily(self, topic: str, search_type: str = "papers") -> str:
        """Search for recent resources using Tavily API"""
        if not self.tavily:
            return ""
        
        try:
            # Build search query based on type
            if search_type == "papers":
                query = f"{topic} research paper 2024 2025 latest tutorial"
            elif search_type == "courses":
                query = f"{topic} online course tutorial free 2024"
            else:
                query = f"{topic} learning resources tutorial documentation"
            
            print(f"Searching Tavily for: {query}")
            
            # Search with Tavily
            response = self.tavily.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True,
                include_domains=["arxiv.org", "github.com", "medium.com", "dev.to", 
                                "coursera.org", "udemy.com", "youtube.com", "freecodecamp.org",
                                "towardsdatascience.com", "paperswithcode.com"]
            )
            
            # Format results
            results = []
            if response.get("answer"):
                results.append(f"**Summary:** {response['answer']}\n")
            
            if response.get("results"):
                results.append("**Recent Resources Found:**\n")
                for i, result in enumerate(response["results"], 1):
                    title = result.get("title", "Untitled")
                    url = result.get("url", "")
                    snippet = result.get("content", "")[:200] + "..." if result.get("content") else ""
                    results.append(f"{i}. **[{title}]({url})**\n   {snippet}\n")
            
            return "\n".join(results) if results else ""
            
        except Exception as e:
            print(f"Tavily search error: {e}")
            return ""
    
    def _build_graph(self):
        workflow = StateGraph(ResourcesState)
        
        # Add nodes
        workflow.add_node("find_resources", self._find_resources)
        
        # Add edges
        workflow.set_entry_point("find_resources")
        workflow.add_edge("find_resources", END)
        
        return workflow.compile()
    
    def _find_resources(self, state: ResourcesState) -> dict:
        """Find and curate learning resources using LLM and Tavily search"""
        topic = state["topic"]
        skill_level = state.get("skill_level", "beginner")
        resource_type = state.get("resource_type", "all")
        
        # Search for recent resources using Tavily
        tavily_results = self._search_tavily(topic, "papers")
        
        if not self.client:
            print("Gemini client not initialized, using fallback for resources")
            return self._fallback_resources(topic, skill_level, resource_type, tavily_results)
        
        # Include Tavily results in the prompt for LLM
        tavily_context = ""
        if tavily_results:
            tavily_context = f"\n\nHere are some recent resources I found online that you should incorporate:\n{tavily_results}"
        
        system_prompt = """You are an expert educational resource curator. Recommend the best learning resources including courses, books, tutorials, and websites. Use emojis and markdown formatting. Indicate if resources are free or paid. When recent resources are provided, incorporate them into your recommendations with proper links."""
        
        type_filter = f" Focus on {resource_type} resources." if resource_type != "all" else ""
        
        user_prompt = f"Recommend the best learning resources for {topic} for a {skill_level} learner.{type_filter} Include online courses, books, video tutorials, practice platforms, and communities. Mark each as free or paid.{tavily_context}"
        
        try:
            print(f"Calling Gemini for resources: {topic}")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            # Validate response
            if response and response.text:
                content = response.text.strip()
                
                # Check if response is valid
                if len(content) > 100:
                    print("Successfully generated resources from Gemini")
                    return {
                        "messages": [AIMessage(content=content)],
                        "resources": content
                    }
                else:
                    print(f"Invalid response from Gemini for resources, using fallback")
                    return self._fallback_resources(topic, skill_level, resource_type, tavily_results)
            else:
                print("Empty response from Gemini for resources, using fallback")
                return self._fallback_resources(topic, skill_level, resource_type, tavily_results)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_resources(topic, skill_level, resource_type, tavily_results)
    
    def _fallback_resources(self, topic: str, skill_level: str, resource_type: str, tavily_results: str = "") -> dict:
        """Generate topic-specific fallback resources when API is unavailable"""
        topic_lower = topic.lower()
        
        # Topic-specific resources
        if any(x in topic_lower for x in ['python']):
            courses = [
                ("Python for Everybody (Coursera)", "Dr. Chuck's famous course", "🆓"),
                ("100 Days of Code (Udemy)", "Angela Yu's comprehensive course", "💰"),
                ("Automate the Boring Stuff", "Free book and course", "🆓"),
                ("Real Python", "In-depth tutorials", "🆓/💰"),
            ]
            youtube = ["Corey Schafer", "Tech With Tim", "sentdex", "Programming with Mosh"]
            books = ["Python Crash Course", "Fluent Python", "Automate the Boring Stuff"]
            practice = ["LeetCode", "HackerRank", "Codewars", "Exercism"]
            docs = ["docs.python.org", "Real Python", "W3Schools Python"]
            
        elif any(x in topic_lower for x in ['javascript', 'js', 'node']):
            courses = [
                ("The Complete JavaScript Course (Udemy)", "Jonas Schmedtmann", "💰"),
                ("JavaScript.info", "Modern JavaScript Tutorial", "🆓"),
                ("freeCodeCamp JavaScript", "Full curriculum", "🆓"),
                ("Frontend Masters", "Expert-led courses", "💰"),
            ]
            youtube = ["Traversy Media", "Web Dev Simplified", "Fireship", "The Net Ninja"]
            books = ["Eloquent JavaScript", "You Don't Know JS", "JavaScript: The Good Parts"]
            practice = ["JavaScript30", "Frontend Mentor", "Codewars", "LeetCode"]
            docs = ["MDN Web Docs", "JavaScript.info", "DevDocs.io"]
            
        elif any(x in topic_lower for x in ['react']):
            courses = [
                ("React - The Complete Guide (Udemy)", "Maximilian Schwarzmüller", "💰"),
                ("React Documentation", "Official React tutorials", "🆓"),
                ("Scrimba React Course", "Interactive learning", "🆓/💰"),
                ("Epic React (Kent C. Dodds)", "Advanced React", "💰"),
            ]
            youtube = ["Web Dev Simplified", "Traversy Media", "Codevolution", "Jack Herrington"]
            books = ["Learning React", "React Up and Running", "Fullstack React"]
            practice = ["React Projects on Frontend Mentor", "Build 50 React Projects", "Codecademy React"]
            docs = ["react.dev", "React Router docs", "Redux Toolkit docs"]
            
        elif any(x in topic_lower for x in ['data science', 'machine learning', 'ml', 'ai', 'deep learning']):
            courses = [
                ("Machine Learning (Coursera)", "Andrew Ng's famous course", "🆓/💰"),
                ("Fast.ai", "Practical deep learning", "🆓"),
                ("Data Science Specialization (Coursera)", "Johns Hopkins", "💰"),
                ("Google ML Crash Course", "Quick introduction", "🆓"),
            ]
            youtube = ["3Blue1Brown", "StatQuest", "Sentdex", "Two Minute Papers"]
            books = ["Hands-On Machine Learning", "Deep Learning (Goodfellow)", "Python for Data Analysis"]
            practice = ["Kaggle", "DrivenData", "Analytics Vidhya", "Google Colab"]
            docs = ["scikit-learn.org", "TensorFlow docs", "PyTorch tutorials"]
            
        elif any(x in topic_lower for x in ['web', 'html', 'css', 'frontend']):
            courses = [
                ("The Odin Project", "Full web dev curriculum", "🆓"),
                ("freeCodeCamp", "Responsive Web Design", "🆓"),
                ("CSS for JavaScript Developers", "Josh Comeau", "💰"),
                ("Frontend Masters", "Expert courses", "💰"),
            ]
            youtube = ["Kevin Powell (CSS)", "Traversy Media", "Web Dev Simplified", "DesignCourse"]
            books = ["HTML & CSS (Jon Duckett)", "CSS Secrets", "Don't Make Me Think"]
            practice = ["Frontend Mentor", "CSS Battle", "100 Days CSS Challenge"]
            docs = ["MDN Web Docs", "CSS-Tricks", "web.dev"]
            
        else:
            # Generic resources
            courses = [
                (f"Search Coursera for '{topic}'", "University courses", "🆓/💰"),
                (f"Search Udemy for '{topic}'", "Practical courses", "💰"),
                (f"Search edX for '{topic}'", "Academic courses", "🆓/💰"),
                ("LinkedIn Learning", "Professional courses", "💰"),
            ]
            youtube = [f"Search: '{topic} tutorial'", f"'{topic} crash course'", f"'{topic} for beginners'"]
            books = [f"Search Amazon for '{topic}' books", "Check Goodreads ratings", "Visit local library"]
            practice = ["Apply concepts in projects", "Join coding challenges", "Contribute to open source"]
            docs = [f"Official {topic} documentation", "DevDocs.io", "Stack Overflow"]
        
        resources = f"""# 📚 Learning Resources: {topic}

> **Skill Level:** {skill_level.capitalize()} | **Resource Focus:** {resource_type.capitalize() if resource_type != 'all' else 'All Types'}

---

## 🎓 Online Courses

| Course | Description | Price |
|--------|-------------|-------|
{"".join([f"| **{c[0]}** | {c[1]} | {c[2]} |" + chr(10) for c in courses])}

---

## 📹 Video Tutorials (YouTube)

{"".join([f"- 🎥 **{yt}**" + chr(10) for yt in youtube])}

**Tip:** Search for "{topic} tutorial for {skill_level}s" for level-appropriate content.

---

## 📚 Recommended Books

{"".join([f"- 📖 **{b}**" + chr(10) for b in books])}

💡 *Check your local library or O'Reilly Safari for free access!*

---

## 💻 Practice Platforms

{"".join([f"- ⌨️ **{p}**" + chr(10) for p in practice])}

---

## 📖 Documentation & References

{"".join([f"- 🔗 **{d}**" + chr(10) for d in docs])}

---

## 👥 Communities

- **Reddit** - r/{topic_lower.replace(' ', '').replace('-', '')} or related subreddits
- **Discord** - Search "{topic} Discord server"
- **Stack Overflow** - Q&A for all technical questions
- **Dev.to** - Developer community and articles

---

## 🚀 Learning Path Suggestion

1. **Start with:** Free courses and YouTube tutorials
2. **Practice:** Use interactive platforms daily
3. **Build:** Create projects to apply knowledge
4. **Connect:** Join communities for help and networking
5. **Level Up:** Invest in premium courses for advanced topics

---
"""
        # Add Tavily search results if available
        if tavily_results:
            resources += f"""
## 🔍 Latest Resources from Web Search

{tavily_results}

---
"""
        
        resources += f"""
*These resources are curated for {skill_level} learners.*
"""
        return {
            "messages": [AIMessage(content=resources)],
            "resources": resources
        }
    
    async def get_resources(self, message: str, topic: str, resource_type: str = "all", session_id: str = "default") -> str:
        """Get curated resources based on user request with conversation memory"""
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "topic": topic,
            "skill_level": "beginner",
            "resource_type": resource_type,
            "resources": None
        }
        
        result = self.graph.invoke(initial_state)
        
        # Save context using windowed memory (like memory.save_context)
        self.save_context(session_id, message, result["resources"])
        
        return result["resources"]
    
    async def get_resources_stream(self, message: str, topic: str, resource_type: str = "all", session_id: str = "default"):
        """Get curated resources with streaming response, including Tavily search and conversation history"""
        if not self.client:
            result = await self.get_resources(message, topic, resource_type, session_id)
            yield result
            return
        
        # Get windowed conversation history (like ConversationBufferWindowMemory with k=3)
        history_messages = self.get_windowed_history(session_id)
        has_history = len(history_messages) > 0
        
        # Search Tavily only for new topic queries (not follow-ups)
        tavily_results = ""
        if not has_history:
            tavily_results = self._search_tavily(topic, "papers")
        
        # System prompt with clear instructions for context-aware responses
        system_prompt = """You are an expert educational resource curator specializing in finding the best learning materials.

IMPORTANT INSTRUCTIONS:
1. When there is conversation history, ALWAYS refer back to it to understand what topic/resources were discussed
2. For follow-up questions like "tell me more", "what about free ones", "explain that", etc., your response MUST be about the SAME TOPIC from the previous messages
3. Use emojis and markdown formatting for better readability
4. Mark resources as 🆓 Free or 💰 Paid
5. Include links when available
6. Be conversational and helpful

The conversation history below shows what was previously discussed. Use it to provide relevant follow-up responses."""
        
        # Build messages with history context
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history for context
        print(f"[Memory] Session: {session_id}, History messages (k={self.k}): {len(history_messages)}")
        for hist_msg in history_messages:
            messages.append(hist_msg)
            print(f"[Memory] Context: {type(hist_msg).__name__} - {str(hist_msg.content)[:80]}...")
        
        # Build user prompt - always include the raw user message
        if has_history:
            # For follow-ups, just use the user's message directly
            # The LLM will use history context to understand what topic we're discussing
            user_prompt = message
        else:
            # For initial queries, provide structured prompt with Tavily results
            tavily_context = ""
            if tavily_results:
                tavily_context = f"\n\nRecent resources found online (incorporate these with proper links):\n{tavily_results}"
            user_prompt = f"I want to learn about: {topic}\n\nPlease recommend the best learning resources including online courses, books, video tutorials, practice platforms, and communities.{tavily_context}"
        
        messages.append(HumanMessage(content=user_prompt))
        print(f"[Memory] User prompt: {user_prompt[:100]}...")
        print(f"[Memory] Total messages in request: {len(messages)}")
        
        # Collect full response for history
        full_response = ""
        
        try:
            response = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Save the ORIGINAL user message (not the formatted prompt) for natural history
            if full_response:
                self.save_context(session_id, message, full_response)
        except Exception as e:
            print(f"Streaming error: {e}")
            result = await self.get_resources(message, topic, resource_type, session_id)
            yield result


class SummarizerAgent:
    """Agent for document summarization and Q&A using RAG with uploaded documents"""
    
    def __init__(self):
        self.name = "Summarizer"
        self.client = client
        self.graph = self._build_graph()
        
        # Import RAG service
        from app.services.rag_service import rag_service
        self.rag_service = rag_service
    
    def _build_graph(self):
        workflow = StateGraph(QAState)
        
        # Add nodes
        workflow.add_node("answer_question", self._answer_question)
        
        # Add edges
        workflow.set_entry_point("answer_question")
        workflow.add_edge("answer_question", END)
        
        return workflow.compile()
    
    def _answer_question(self, state: QAState) -> dict:
        """Answer user's question using Gemini"""
        question = state["question"]
        
        # If client is not available, use fallback
        if not self.client:
            print("Gemini client not available, using fallback for Q&A")
            return self._fallback_answer(question)
        
        system_prompt = """You are an expert educator and tutor. Answer questions clearly with examples, code snippets when relevant, and practical explanations. Use markdown formatting."""
        
        user_prompt = f"Answer this question comprehensively: {question}"
        
        try:
            print(f"Calling Gemini API for Q&A: {question[:50]}...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            # Validate response
            if response and response.text:
                content = response.text.strip()
                
                # Check if response is valid
                if len(content) > 50:
                    print("Successfully generated answer from Gemini")
                    return {
                        "messages": [AIMessage(content=content)],
                        "answer": content
                    }
                else:
                    print(f"Invalid response from Gemini for Q&A, using fallback")
                    return self._fallback_answer(question)
            else:
                print("Empty response from Gemini for Q&A, using fallback")
                return self._fallback_answer(question)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_answer(question)
    
    def _fallback_answer(self, question: str) -> dict:
        """Fallback answer when API is unavailable"""
        answer = f"""# 💡 Your Question

> {question}

---

## 📝 Response

Thank you for your question! Unfortunately, I'm currently experiencing high demand and cannot provide a detailed AI-generated answer at this moment.

### 🔍 Here's what you can do:

1. **Search Online**
   - Google your question for immediate answers
   - Check Stack Overflow for programming questions
   - Visit official documentation

2. **Learning Resources**
   - MDN Web Docs (for web development)
   - Official language documentation
   - YouTube tutorials

3. **Community Help**
   - Post on Stack Overflow
   - Ask in relevant Discord/Slack communities
   - Check Reddit communities

4. **Try Again Later**
   - The AI service will be available again shortly
   - Please retry in a few minutes

---

*Note: The AI quota has been temporarily exceeded. Please try again later for a detailed AI-powered answer.*
"""
        return {
            "messages": [AIMessage(content=answer)],
            "answer": answer
        }
    
    async def answer(self, question: str, session_id: str = "default") -> str:
        """Answer a user's question using RAG if documents are uploaded"""
        # Check if user has uploaded documents
        if self.rag_service.get_document_count(session_id) > 0:
            # Use RAG pipeline for document-based Q&A
            return await self.rag_service.answer(question, session_id)
        
        # Fallback to regular LLM if no documents uploaded
        initial_state = {
            "messages": [HumanMessage(content=question)],
            "question": question,
            "context": None,
            "answer": None
        }
        
        result = self.graph.invoke(initial_state)
        return result["answer"]
    
    async def answer_stream(self, question: str, session_id: str = "default"):
        """Answer a question with streaming response using RAG"""
        # Check if user has uploaded documents - use RAG pipeline
        if self.rag_service.get_document_count(session_id) > 0:
            async for chunk in self.rag_service.answer_stream(question, session_id):
                yield chunk
            return
        
        # Fallback to regular LLM if no documents uploaded
        if not self.client:
            result = await self.answer(question, session_id)
            yield result
            return
        
        system_prompt = """You are an expert educator and tutor. Answer questions clearly with examples, code snippets when relevant, and practical explanations. Use markdown formatting.

Note: No documents have been uploaded yet. For document-based Q&A, please upload PDF, DOCX, or TXT files first."""
        
        user_prompt = f"Answer this question comprehensively: {question}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"Streaming error: {e}")
            result = await self.answer(question, session_id)
            yield result
    
    async def upload_document(self, file_content: bytes, filename: str, session_id: str) -> Dict:
        """Upload a document for RAG processing"""
        return await self.rag_service.process_document(file_content, filename, session_id)
    
    def get_uploaded_documents(self, session_id: str) -> List[str]:
        """Get list of uploaded documents for a session"""
        return self.rag_service.get_session_documents(session_id)
    
    def clear_session(self, session_id: str):
        """Clear session data including documents and history"""
        self.rag_service.clear_session(session_id)


class QuizAgent:
    """
    Interactive Q&A Agent for interview prep, exam preparation, and knowledge testing.
    
    Flow:
    1. User provides domain, purpose, and difficulty level
    2. Agent generates questions based on these parameters
    3. User answers questions
    4. Agent rates answers (1-5) and provides feedback
    5. If rating < 3, user must improve to proceed
    """
    

    def __init__(self):
        self.name = "Question Answering System"
        self.client = client
        # Persistence handled by agent_chat_service
        from app.services.agent_chat_service import agent_chat_service
        self.chat_service = agent_chat_service
    
    async def _get_session(self, session_id: str) -> Dict:
        """Get session data from DB (ensuring chat exists)"""
        try:
            user_id, chat_id = session_id.split("_")
            
            # Ensure chat session exists in DB
            await self.chat_service.get_or_create_chat(
                user_id=user_id,
                agent_type="quiz",
                chat_id=chat_id,
                initial_message="Start Quiz"
            )
            
            # Now safe to get session data
            data = await self.chat_service.get_session_data(chat_id, user_id)
            
            # Initialize default structure if empty
            if not data:
                data = {
                    "domain": None,
                    "purpose": None,
                    "difficulty": None,
                    "score": 0,
                    "questions_asked": 0,
                    "current_question": None,
                    "current_options": {},
                    "correct_answer": None,
                    "explanation": "",
                    "awaiting_answer": False,
                    "needs_retry": False,
                    "history": []
                }
                # Save initial state
                await self.chat_service.update_session_data(chat_id, user_id, data)
            return data
        except ValueError:
            print(f"Invalid session_id format: {session_id}")
            return {}
        except Exception as e:
            print(f"Error getting session: {e}")
            return {}

    async def _save_session(self, session_id: str, data: Dict):
        """Save session data to DB"""
        try:
            user_id, chat_id = session_id.split("_")
            await self.chat_service.update_session_data(chat_id, user_id, data)
        except Exception as e:
            print(f"Error saving session: {e}")

    async def start_session(self, session_id: str, domain: str, purpose: str, difficulty: str) -> str:
        """Initialize a quiz session with user preferences"""
        session = await self._get_session(session_id)
        session["domain"] = domain
        session["purpose"] = purpose
        session["difficulty"] = difficulty
        session["score"] = 0
        session["questions_asked"] = 0
        session["current_question"] = None
        session["current_options"] = {}
        session["correct_answer"] = None
        session["explanation"] = ""
        session["awaiting_answer"] = False
        session["needs_retry"] = False
        session["history"] = []
        
        await self._save_session(session_id, session)
        
        purpose_text = {
            "interview": "interview preparation",
            "exam": "exam preparation", 
            "knowledge": "knowledge testing"
        }.get(purpose, purpose)
        
        return f"""🎯 **Quiz Session Started!**

**Domain:** {domain}
**Purpose:** {purpose_text.title()}
**Difficulty:** {difficulty.title()}

I'll ask you questions tailored for {purpose_text}. After each answer, I'll rate your response (1-5 stars) and provide feedback.

⚠️ **Note:** You need to answer correctly to proceed to the next question.

Type **"start"** when you're ready for your first question!"""
    
    async def generate_question(self, session_id: str) -> str:
        """Generate a multiple choice question based on session parameters"""
        session = await self._get_session(session_id)
        
        if not session.get("domain"):
            return "Please start a session first by providing domain, purpose, and difficulty level."
        
        domain = session["domain"]
        purpose = session["purpose"]
        difficulty = session["difficulty"]
        questions_asked = session["questions_asked"]
        
        # Build context from previous questions to avoid repetition
        prev_questions = [q["question"] for q in session.get("history", [])[-5:]] if session.get("history") else []
        prev_context = "\\n".join([f"- {q}" for q in prev_questions]) if prev_questions else "None yet"
        
        system_prompt = f"""You are an expert examiner for {domain}.
Generate exactly ONE multiple choice question (MCQ) with 4 options.

IMPORTANT RULES:
- Difficulty level: {difficulty}
- Create a clear, concise question
- Provide exactly 4 options labeled A, B, C, D
- Only ONE option should be correct
- Make wrong options plausible but clearly incorrect
- The question should test {purpose} knowledge

Previous questions asked (avoid repeating similar topics):
{prev_context}

FORMAT YOUR RESPONSE AS A VALID JSON OBJECT:
{{
  "question": "The question text",
  "options": {{
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text"
  }},
  "correct_answer": "A",
  "explanation": "Brief explanation of why the answer is correct"
}}"""
        
        if not self.client:
            # Fallback MCQ questions
            question = f"What is the primary purpose of {domain}?"
            options = {
                "A": f"To make applications faster",
                "B": f"To organize and structure code effectively",
                "C": f"To replace all other technologies",
                "D": f"To increase hardware requirements"
            }
            correct = "B"
            explanation = f"{domain} helps organize and structure code for better maintainability."
        else:
            try:
                # Import json for parsing
                import json
                from google.genai import types
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{system_prompt}\n\nGenerate a {difficulty} MCQ for {domain} ({purpose})",
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                # Parse the JSON response
                try:
                    quiz_data = json.loads(response.text.strip())
                    question = quiz_data.get("question", "Error parsing question")
                    options = quiz_data.get("options", {"A": "Error", "B": "Error", "C": "Error", "D": "Error"})
                    correct = quiz_data.get("correct_answer", "A").upper()
                    explanation = quiz_data.get("explanation", "No explanation provided.")
                    
                    # Validate options
                    if not isinstance(options, dict) or not all(k in options for k in ["A", "B", "C", "D"]):
                        raise ValueError("Invalid options format")
                        
                except Exception as parse_error:
                    print(f"JSON parsing error: {parse_error}")
                    # Fallback parsing if JSON fails or is malformed
                    question = "Error generating question. Please try 'next' again."
                    options = {"A": "Retry", "B": "Retry", "C": "Retry", "D": "Retry"}
                    correct = "A"
                    explanation = "An error occurred during generation."

            except Exception as e:
                print(f"Error generating MCQ: {e}")
                question = f"What is {domain}?"
                options = {
                    "A": "A framework",
                    "B": "A library",
                    "C": "A concept/technology",
                    "D": "None of the above"
                }
                correct = "C"
                explanation = f"{domain} is a concept/technology used in software development."
        
        # Store question data in session
        session["current_question"] = question
        session["current_options"] = options
        session["correct_answer"] = correct
        session["explanation"] = explanation
        session["awaiting_answer"] = True
        session["questions_asked"] += 1
        
        await self._save_session(session_id, session)
        
        return f"""📝 **Question {session["questions_asked"]}** ({difficulty.title()})

{question}

**A)** {options["A"]}
**B)** {options["B"]}
**C)** {options["C"]}
**D)** {options["D"]}

---
*Type your answer: A, B, C, or D*"""
    
    async def evaluate_answer(self, session_id: str, user_answer: str) -> str:
        """Evaluate user's MCQ answer"""
        session = await self._get_session(session_id)
        
        if not session.get("current_question"):
            return "No active question. Type **'next'** to get a new question."
        
        question = session["current_question"]
        options = session.get("current_options", {})
        correct = session.get("correct_answer", "A")
        explanation = session.get("explanation", "")
        
        # Normalize user answer
        user_choice = user_answer.strip().upper()
        if user_choice not in ["A", "B", "C", "D"]:
            # Try to extract just the letter
            for char in user_answer.upper():
                if char in ["A", "B", "C", "D"]:
                    user_choice = char
                    break
            else:
                return "⚠️ Please enter a valid option: **A**, **B**, **C**, or **D**"
        
        is_correct = user_choice == correct
        
        # Store in history
        history = session.get("history", [])
        history.append({
            "question": question,
            "answer": user_choice,
            "correct_answer": correct,
            "is_correct": is_correct
        })
        session["history"] = history
        
        if is_correct:
            session["score"] += 1
            session["needs_retry"] = False
            session["awaiting_answer"] = False
            session["current_question"] = None
            
            result = f"""## ✅ Correct!

**Your Answer:** {user_choice}) {options.get(user_choice, '')}

### 📖 Explanation
{explanation}

---
🎉 **Great job!** Your current score: **{session["score"]}/{session["questions_asked"]}**

Type **'next'** for the next question or **'score'** to see your progress."""
        
        else:
            session["needs_retry"] = True
            session["awaiting_answer"] = True
            
            result = f"""## ❌ Incorrect

**Your Answer:** {user_choice}) {options.get(user_choice, '')}
**Correct Answer:** {correct}) {options.get(correct, '')}

### 📖 Explanation
{explanation}

---
⚠️ **Try to remember this for next time!**

Type **'next'** to continue to the next question or **'score'** to see your progress."""
            
            # Allow moving to next question even if wrong (but don't add score)
            session["needs_retry"] = False
            session["awaiting_answer"] = False
            session["current_question"] = None
        
        await self._save_session(session_id, session)
        return result
    
    async def get_score(self, session_id: str) -> str:
        """Get current score and progress"""
        session = await self._get_session(session_id)
        
        if session.get("questions_asked", 0) == 0:
            return "No questions answered yet. Start your session first!"
        
        correct = session["score"]
        total = session["questions_asked"]
        percentage = (correct / total) * 100 if total > 0 else 0
        
        performance = "Excellent!" if percentage >= 90 else \
                      "Great!" if percentage >= 75 else \
                      "Good" if percentage >= 60 else \
                      "Needs Improvement"
        
        return f"""## Your Progress

**Domain:** {session.get("domain")}
**Purpose:** {session.get("purpose", "").title()}
**Difficulty:** {session.get("difficulty", "").title()}

---

| Metric | Value |
|--------|-------|
| Questions Answered | {total} |
| Correct Answers | {correct} |
| Wrong Answers | {total - correct} |
| Accuracy | {int(percentage)}% |
| Performance | {performance} |

---
Type **'next'** to continue or **'end'** to finish the session."""
    
    async def end_session(self, session_id: str) -> str:
        """End the quiz session and show final results"""
        session = await self._get_session(session_id)
        
        if session.get("questions_asked", 0) == 0:
            return "No session to end. Start a new session to begin!"
        
        correct = session.get("score", 0)
        total = session.get("questions_asked", 0)
        percentage = (correct / total) * 100 if total > 0 else 0
        
        # Performance grade based on percentage
        if percentage >= 90:
            grade = "A+"
            message = "Outstanding performance! You've demonstrated excellent mastery."
        elif percentage >= 80:
            grade = "A"
            message = "Excellent work! You have a strong understanding."
        elif percentage >= 70:
            grade = "B+"
            message = "Great job! You're well-prepared."
        elif percentage >= 60:
            grade = "B"
            message = "Good performance! Keep practicing to improve further."
        elif percentage >= 50:
            grade = "C"
            message = "Fair performance. More practice is recommended."
        else:
            grade = "D"
            message = "You need more study. Review the topics and try again."
        
        result = f"""## Session Complete!

### Final Results for {session.get("domain", "Unknown")}

| Metric | Value |
|--------|-------|
| Purpose | {session.get("purpose", "").title()} |
| Difficulty | {session.get("difficulty", "").title()} |
| Questions Answered | {total} |
| Correct Answers | {correct} |
| Wrong Answers | {total - correct} |
| Accuracy | {int(percentage)}% |
| **Grade** | **{grade}** |

---

### Feedback
{message}

---
*Start a new session anytime by selecting domain, purpose, and difficulty!*
"""
        
        # Clear session (mark as inactive/reset in DB)
        empty_data = {
            "domain": None,
            "purpose": None,
            "difficulty": None,
            "score": 0,
            "questions_asked": 0,
            "current_question": None,
            "current_options": {},
            "correct_answer": None,
            "explanation": "",
            "awaiting_answer": False,
            "needs_retry": False,
            "history": []
        }
        await self._save_session(session_id, empty_data)
        
        return result
    
    async def process_message(self, message: str, session_id: str) -> str:
        """Process user message and determine action"""
        session = await self._get_session(session_id)
        msg_lower = message.lower().strip()
        
        # Handle commands
        if msg_lower == "start" or msg_lower == "next":
            return await self.generate_question(session_id)
        
        elif msg_lower == "score":
            return await self.get_score(session_id)
        
        elif msg_lower == "end" or msg_lower == "finish" or msg_lower == "quit":
            return await self.end_session(session_id)
        
        elif msg_lower == "help":
            return """## 🆘 Quiz Commands

| Command | Description |
|---------|-------------|
| **start** | Get your first question |
| **next** | Get the next question |
| **score** | View your current progress |
| **end** | End the session and see final results |
| **help** | Show this help message |

---
*To answer a question, type **A**, **B**, **C**, or **D**!*"""
        
        # If awaiting answer, evaluate it
        elif session["awaiting_answer"] and session["current_question"]:
            return await self.evaluate_answer(session_id, message)
        
        # No active session or question
        elif not session["domain"]:
            return "Please start a session first by filling out the form with domain, purpose, and difficulty level."
        
        else:
            return "Type **'next'** to get a question, **'score'** to see progress, or **'end'** to finish."
    
    async def process_message_stream(self, message: str, session_id: str):
        """Stream the response for a message"""
        response = await self.process_message(message, session_id)
        # Stream in chunks for better UX
        chunk_size = 50
        for i in range(0, len(response), chunk_size):
            yield response[i:i + chunk_size]


class MathSolverAgent:
    """
    Advanced Math Problem Solver Agent with Multi-Agent Architecture.
    
    Flow:
    User Input -> Math Classifier Agent -> Reasoning Agent (LLaMA) -> 
    Tool Executor Agent (SymPy/NumPy) -> Solution Formatter Agent -> Final Answer
    
    Supports: Algebra, Calculus, Probability, Linear Algebra, Geometry, Trigonometry, Statistics
    """
    
    def __init__(self):
        self.name = "Math Problem Solver"
        self.client = client
        self.graph = self._build_graph()
        
        # Initialize mathematical tools
        self._setup_math_tools()
        
        # Conversation history per session
        self.session_histories: Dict[str, ChatMessageHistory] = {}
        self.k = 3  # Keep last k conversation turns
    
    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        """Get or create ChatMessageHistory for a session"""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = ChatMessageHistory()
        return self.session_histories[session_id]
    
    def get_windowed_history(self, session_id: str) -> List:
        """Get last k conversation turns"""
        history = self.get_session_history(session_id)
        messages = history.messages
        return messages[-(self.k * 2):] if len(messages) > self.k * 2 else messages
    
    def save_context(self, session_id: str, user_input: str, ai_output: str):
        """Save conversation context"""
        history = self.get_session_history(session_id)
        history.add_user_message(user_input)
        history.add_ai_message(ai_output)
        print(f"[Math Memory] Saved context for session {session_id}. Total messages: {len(history.messages)}")
    
    def _setup_math_tools(self):
        """Setup SymPy and NumPy for mathematical computations"""
        try:
            import sympy as sp
            self.sympy = sp
            self.sympy_available = True
        except ImportError:
            self.sympy_available = False
            print("Warning: SymPy not available for symbolic math")
        
        try:
            import numpy as np
            self.numpy = np
            self.numpy_available = True
        except ImportError:
            self.numpy_available = False
            print("Warning: NumPy not available for numerical math")
    
    def _build_graph(self):
        """Build the LangGraph workflow for multi-agent math problem solving"""
        workflow = StateGraph(MathProblemState)
        
        # Add nodes for each agent in the pipeline
        workflow.add_node("classifier_agent", self._classify_problem)
        workflow.add_node("reasoning_agent", self._reason_through_problem)
        workflow.add_node("tool_executor_agent", self._execute_with_tools)
        workflow.add_node("formatter_agent", self._format_solution)
        
        # Define edges for the multi-agent flow
        workflow.set_entry_point("classifier_agent")
        workflow.add_edge("classifier_agent", "reasoning_agent")
        workflow.add_edge("reasoning_agent", "tool_executor_agent")
        workflow.add_edge("tool_executor_agent", "formatter_agent")
        workflow.add_edge("formatter_agent", END)
        
        return workflow.compile()
    
    def _classify_problem(self, state: MathProblemState) -> dict:
        """
        AGENT 1: Math Classifier Agent
        Classifies the problem into categories for specialized handling
        """
        problem = state["problem"]
        problem_lower = problem.lower()
        
        # Detailed classification with sub-categories
        classifications = {
            "Algebra": ["solve", "equation", "factor", "simplify", "expand", "quadratic", "polynomial", "linear", "x =", "find x", "variable"],
            "Calculus": ["derivative", "integral", "limit", "differentiate", "integrate", "d/dx", "dy/dx", "antiderivative", "rate of change", "slope"],
            "Probability": ["probability", "chance", "odds", "expected value", "random", "dice", "coin", "cards", "permutation", "combination", "factorial"],
            "Linear Algebra": ["matrix", "matrices", "determinant", "vector", "eigenvalue", "eigenvector", "transpose", "inverse matrix", "linear transformation"],
            "Geometry": ["triangle", "circle", "square", "rectangle", "area", "perimeter", "volume", "angle", "polygon", "radius", "diameter", "pythagorean"],
            "Trigonometry": ["sin", "cos", "tan", "sine", "cosine", "tangent", "radian", "degree", "arcsin", "arccos", "arctan", "trigonometric"],
            "Statistics": ["mean", "median", "mode", "standard deviation", "variance", "average", "data", "distribution", "sample", "population"]
        }
        
        problem_type = "General Mathematics"
        confidence = 0
        
        for category, keywords in classifications.items():
            matches = sum(1 for kw in keywords if kw in problem_lower)
            if matches > confidence:
                confidence = matches
                problem_type = category
        
        return {"problem_type": problem_type}
    
    def _reason_through_problem(self, state: MathProblemState) -> dict:
        """
        AGENT 2: Reasoning Agent (LLaMA)
        Analyzes the problem and creates a solution strategy
        """
        problem = state["problem"]
        problem_type = state.get("problem_type", "General Mathematics")
        
        if not self.client:
            return {
                "steps": ["Gemini client not available"],
                "final_answer": "Error: Cannot reason without Gemini",
                "explanation": "Please ensure Google API Key is set."
            }
        
        reasoning_prompt = f"""You are an expert {problem_type} specialist. Analyze this problem and create a detailed solution plan.

PROBLEM: {problem}

Provide:
1. What type of problem this is
2. What formulas or methods are needed
3. Step-by-step approach to solve it
4. Expected form of the answer

Be specific and mathematical. Output in plain text only."""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a math reasoning expert. Analyze problems and plan solutions.\n\n{reasoning_prompt}"
            )
            reasoning = response.text.strip()
            
            return {
                "steps": [reasoning],
                "explanation": reasoning
            }
        except Exception as e:
            return {
                "steps": [f"Reasoning error: {str(e)}"],
                "explanation": f"Error during reasoning: {str(e)}"
            }
    
    def _execute_with_tools(self, state: MathProblemState) -> dict:
        """
        AGENT 3: Tool Executor Agent
        Uses SymPy (symbolic) and NumPy (numerical) for calculations
        """
        problem = state["problem"]
        problem_type = state.get("problem_type", "General Mathematics")
        
        tool_result = None
        
        # Try SymPy for symbolic calculations
        if self.sympy_available:
            tool_result = self._try_sympy_solve(problem, problem_type)
        
        # Fallback to NumPy for numerical problems
        if tool_result is None and self.numpy_available:
            tool_result = self._try_numpy_solve(problem, problem_type)
        
        if tool_result:
            return {
                "final_answer": str(tool_result),
                "steps": state.get("steps", []) + [f"Tool calculated: {tool_result}"]
            }
        
        return state
    
    def _try_sympy_solve(self, problem: str, problem_type: str):
        """Attempt to solve using SymPy"""
        if not self.sympy_available:
            return None
        
        sp = self.sympy
        problem_lower = problem.lower()
        
        try:
            # Extract numbers and try to parse equations
            import re
            
            # Algebra: Solve equations
            if problem_type == "Algebra":
                # Look for patterns like "x^2 + 5x + 6 = 0" or "2x + 3 = 7"
                x = sp.Symbol('x')
                
                # Try to find and solve quadratic equations
                quad_match = re.search(r'x\^?2?\s*[\+\-]\s*\d*x?\s*[\+\-]?\s*\d*\s*=\s*0', problem_lower)
                if quad_match or "quadratic" in problem_lower:
                    # Extract coefficients if possible
                    nums = re.findall(r'[-+]?\d+', problem)
                    if len(nums) >= 2:
                        try:
                            a = int(nums[0]) if len(nums) > 0 else 1
                            b = int(nums[1]) if len(nums) > 1 else 0
                            c = int(nums[2]) if len(nums) > 2 else 0
                            solutions = sp.solve(a*x**2 + b*x + c, x)
                            return solutions
                        except:
                            pass
            
            # Calculus: Derivatives
            if problem_type == "Calculus":
                x = sp.Symbol('x')
                if "derivative" in problem_lower or "differentiate" in problem_lower:
                    # Try to parse simple expressions
                    if "x^2" in problem or "x**2" in problem:
                        expr = x**2
                        nums = re.findall(r'\d+', problem)
                        if nums:
                            coef = int(nums[0])
                            expr = coef * x**2
                        return sp.diff(expr, x)
                    elif "x^3" in problem or "x**3" in problem:
                        return sp.diff(x**3, x)
                
                if "integral" in problem_lower or "integrate" in problem_lower:
                    if "x^2" in problem or "x**2" in problem:
                        return sp.integrate(x**2, x)
            
            # Probability: Basic calculations
            if problem_type == "Probability":
                if "factorial" in problem_lower:
                    nums = re.findall(r'\d+', problem)
                    if nums:
                        n = int(nums[0])
                        return sp.factorial(n)
                
                if "combination" in problem_lower or "choose" in problem_lower:
                    nums = re.findall(r'\d+', problem)
                    if len(nums) >= 2:
                        n, r = int(nums[0]), int(nums[1])
                        return sp.binomial(n, r)
            
            # Linear Algebra: Determinant
            if problem_type == "Linear Algebra":
                if "determinant" in problem_lower:
                    # Extract matrix values
                    nums = re.findall(r'[-+]?\d+', problem)
                    if len(nums) == 4:
                        a, b, c, d = [int(n) for n in nums[:4]]
                        matrix = sp.Matrix([[a, b], [c, d]])
                        return matrix.det()
            
        except Exception as e:
            print(f"SymPy error: {e}")
        
        return None
    
    def _try_numpy_solve(self, problem: str, problem_type: str):
        """Attempt numerical calculations using NumPy"""
        if not self.numpy_available:
            return None
        
        np = self.numpy
        problem_lower = problem.lower()
        
        try:
            import re
            nums = re.findall(r'[-+]?\d*\.?\d+', problem)
            
            # Statistics calculations
            if problem_type == "Statistics" and nums:
                numbers = [float(n) for n in nums]
                
                if "mean" in problem_lower or "average" in problem_lower:
                    return round(np.mean(numbers), 4)
                elif "median" in problem_lower:
                    return round(np.median(numbers), 4)
                elif "standard deviation" in problem_lower:
                    return round(np.std(numbers), 4)
                elif "variance" in problem_lower:
                    return round(np.var(numbers), 4)
            
            # Basic arithmetic
            if len(nums) >= 2:
                a, b = float(nums[0]), float(nums[1])
                if "add" in problem_lower or "sum" in problem_lower:
                    return a + b
                elif "subtract" in problem_lower or "difference" in problem_lower:
                    return a - b
                elif "multiply" in problem_lower or "product" in problem_lower:
                    return a * b
                elif "divide" in problem_lower:
                    return round(a / b, 4) if b != 0 else "undefined"
        
        except Exception as e:
            print(f"NumPy error: {e}")
        
        return None
    
    def _format_solution(self, state: MathProblemState) -> dict:
        """
        AGENT 4: Solution Formatter Agent
        Formats the final solution in a clean, readable format
        """
        problem = state["problem"]
        problem_type = state.get("problem_type", "General Mathematics")
        tool_answer = state.get("final_answer")
        reasoning = state.get("explanation", "")
        
        if not self.client:
            return state
        
        # Build context from tool results
        tool_context = ""
        if tool_answer and tool_answer != "Error":
            tool_context = f"\n\nVERIFIED CALCULATION RESULT: {tool_answer}"
        
        formatter_prompt = f"""You are a Solution Formatter. Present this math solution clearly.

PROBLEM TYPE: {problem_type}
PROBLEM: {problem}
{tool_context}

Create a beautiful, well-formatted solution following this EXACT structure:

---

**Problem**

[Restate the problem clearly]

---

**Problem Type:** {problem_type}

---

**Solution**

**Step 1:** [First step with explanation]

**Step 2:** [Second step with explanation]

[Continue as needed...]

---

**Answer**

[State the final answer clearly - use the verified calculation if provided]

---

**Method Used**

[Brief explanation of the approach]

---

RULES:
- NO LaTeX, NO $, NO \\boxed{{}}
- Write fractions as a/b
- Write exponents as x^2
- Write square roots as sqrt(x) or √
- Keep it clean and readable
- If a verified calculation was provided, USE THAT as the answer"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a math solution formatter. Create clean, well-structured solutions.\n\n{formatter_prompt}"
            )
            formatted = response.text.strip()
            
            return {
                "explanation": formatted,
                "final_answer": tool_answer or "See solution above"
            }
        except Exception as e:
            return {
                "explanation": f"Formatting error: {str(e)}",
                "final_answer": tool_answer or "Error"
            }
    
    async def solve(self, problem: str) -> str:
        """Solve a math problem using the multi-agent pipeline"""
        initial_state = {
            "messages": [],
            "problem": problem,
            "problem_type": None,
            "steps": None,
            "final_answer": None,
            "explanation": None
        }
        
        result = self.graph.invoke(initial_state)
        return result.get("explanation", "Unable to solve the problem.")
    
    async def solve_stream(self, problem: str, session_id: str = "default"):
        """Solve a math problem with streaming response"""
        if not self.client:
            yield "Error: Gemini client not initialized. Please ensure Google API Key is set."
            return
        
        # Get conversation history for context
        history_messages = self.get_windowed_history(session_id)
        has_history = len(history_messages) > 0
        print(f"[Math Memory] Session: {session_id}, History: {len(history_messages)} messages")
        
        # AGENT 1: Classify the problem
        yield "**Analyzing problem type...**\n\n"
        
        problem_lower = problem.lower()
        problem_type = "General Mathematics"
        
        classifications = {
            "Algebra": ["solve", "equation", "factor", "simplify", "quadratic", "polynomial", "x ="],
            "Calculus": ["derivative", "integral", "limit", "differentiate", "integrate"],
            "Probability": ["probability", "chance", "permutation", "combination", "factorial"],
            "Linear Algebra": ["matrix", "determinant", "vector", "eigenvalue"],
            "Geometry": ["triangle", "circle", "area", "perimeter", "volume", "angle"],
            "Trigonometry": ["sin", "cos", "tan", "degree", "radian"],
            "Statistics": ["mean", "median", "mode", "standard deviation", "variance"]
        }
        
        for category, keywords in classifications.items():
            if any(kw in problem_lower for kw in keywords):
                problem_type = category
                break
        
        yield f"**Problem Type:** {problem_type}\n\n"
        
        # AGENT 3: Try tool execution first
        tool_result = None
        if self.sympy_available:
            tool_result = self._try_sympy_solve(problem, problem_type)
            if tool_result:
                yield f"**Tool Verification:** SymPy calculated -> `{tool_result}`\n\n"
        
        if tool_result is None and self.numpy_available:
            tool_result = self._try_numpy_solve(problem, problem_type)
            if tool_result:
                yield f"**Tool Verification:** NumPy calculated -> `{tool_result}`\n\n"
        
        yield "---\n\n"
        
        # AGENT 2 & 4: Reasoning and formatting combined in stream
        tool_context = f"\nVERIFIED ANSWER: {tool_result}" if tool_result else ""
        
        solve_prompt = f"""Solve this {problem_type} problem with clear steps.

PROBLEM: {problem}
{tool_context}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

**Problem**

[Restate the problem]

---

**Solution**

**Step 1:** [Explanation and work]

**Step 2:** [Explanation and work]

[Continue as needed...]

---

**Answer**

[Final answer - {"use the VERIFIED ANSWER: " + str(tool_result) if tool_result else "calculate carefully"}]

---

**Key Concept**

[Brief explanation]

---

IMPORTANT RULES:
- NO LaTeX ($, \\boxed{{}}, etc.) - FORBIDDEN
- Write fractions as: a/b
- Write exponents as: x^2, x^3
- Write square roots as: sqrt(x) or √x
- Write pi as: π or pi
- Keep everything in PLAIN TEXT"""

        messages = [
            SystemMessage(content="You are an expert math tutor. Solve problems step-by-step in clean plain text. If there's conversation history, you can reference previous problems or solutions when relevant.")
        ]
        
        # Add conversation history for context
        for hist_msg in history_messages:
            messages.append(hist_msg)
        
        messages.append(HumanMessage(content=solve_prompt))
        
        full_response = ""
        try:
            response = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=f"You are an expert math tutor. Solve problems step-by-step in clean plain text.\n\n{solve_prompt}"
            )
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Save context for history
            if full_response:
                self.save_context(session_id, problem, full_response)
        except Exception as e:
            print(f"Streaming error in math solver: {e}")
            result = await self.solve(problem)
            yield result
    
    async def solve_from_image_stream(self, image_base64: str, session_id: str = "default"):
        """
        Solve a math problem from an image using base64 encoding.
        Sends the image directly to the vision-capable LLM (llava).
        """
        # Use Gemini for image processing (it supports vision)
        if not self.client:
            yield "Error: Gemini client not initialized."
            return
        
        # Get conversation history
        history_messages = self.get_windowed_history(session_id)
        
        vision_prompt = """You are an expert mathematics tutor. Look at this image of a math problem.

YOUR TASK:
1. First, read and understand EXACTLY what math problem is shown in the image
2. Identify the type of problem (algebra, calculus, geometry, etc.)
3. Solve it step by step using Chain of Thought reasoning
4. Show all your work clearly

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

---

**Problem from Image**

[Write out the exact problem you see in the image]

---

**Problem Type:** [Category]

---

**Solution**

**Step 1:** [Explanation and calculation]

**Step 2:** [Explanation and calculation]

[Continue as needed...]

---

**Answer**

[Clear final answer]

---

**Key Concept**

[Brief explanation of the method used]

---

IMPORTANT RULES:
- NO LaTeX ($, \\boxed{}, etc.) - FORBIDDEN
- Write fractions as: a/b
- Write exponents as: x^2, x^3
- Write square roots as: sqrt(x) or √x
- Keep everything in PLAIN TEXT
- First describe what you see in the image before solving"""

        try:
            # Create content with text and image for Gemini
            from google import genai
            from google.genai import types
            
            # Decode base64 image
            import base64
            image_bytes = base64.b64decode(image_base64)
            
            # Create content with text and image
            # Note: Gemini 2.0 Flash supports interleaved text and image
            
            response = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=[
                    vision_prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                ]
            )
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Save context for history
            if full_response:
                self.save_context(session_id, "[Image Problem]", full_response)
                
        except Exception as e:
            print(f"Vision streaming error in math solver: {e}")
            # Fallback message if vision doesn't work
            yield f"""
---

**Vision Processing Note**

Unable to process the image directly. Error: {str(e)}

**Suggestions:**
- Make sure you're using a vision-capable model (e.g., llama3.2-vision, llava)
- Try typing the problem manually instead
- Ensure the image is clear and readable

---
"""


class JobSearchAgent:
    """
    Job Search Agent using Tavily API.
    
    Searches for recent job listings from job boards and career sites.
    Provides formatted job results with links to apply.
    """
    
    def __init__(self):
        self.name = "Job Search"
        self.tavily = tavily_client
        # self.llm = llm # Not used for job search
        
        # Conversation history per session
        self.session_histories: Dict[str, ChatMessageHistory] = {}
        self.k = 3  # Keep last k conversation turns
    
    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        """Get or create ChatMessageHistory for a session"""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = ChatMessageHistory()
        return self.session_histories[session_id]
    
    def get_windowed_history(self, session_id: str) -> List:
        """Get last k conversation turns"""
        history = self.get_session_history(session_id)
        messages = history.messages
        return messages[-(self.k * 2):] if len(messages) > self.k * 2 else messages
    
    def save_context(self, session_id: str, user_input: str, ai_output: str):
        """Save conversation context"""
        history = self.get_session_history(session_id)
        history.add_user_message(user_input)
        history.add_ai_message(ai_output)
        print(f"[Jobs Memory] Saved context for session {session_id}. Total messages: {len(history.messages)}")
    
    async def search_jobs(self, query: str, location: str = "") -> Dict:
        """
        Search for jobs using Tavily API
        
        Args:
            query: Job title or keywords (e.g., "python developer", "data scientist")
            location: City or region (e.g., "London", "New York")
        
        Returns:
            Dictionary with job listings
        """
        if not self.tavily:
            return {
                "success": False,
                "error": "Tavily client not initialized",
                "jobs": []
            }
        
        # Build search query for recent job vacancies only
        search_query = f"{query} jobs hiring now open positions apply"
        if location:
            search_query += f" in {location}"
        search_query += " 2026 vacancies available"
        
        try:
            # Use Tavily to search for recent job listings
            results = self.tavily.search(
                query=search_query,
                search_depth="advanced",
                max_results=10,
                days=7,  # Only get results from the last 7 days
                include_domains=[
                    "linkedin.com/jobs",
                    "indeed.com",
                    "glassdoor.com",
                    "monster.com",
                    "ziprecruiter.com",
                    "dice.com",
                    "careers.google.com",
                    "amazon.jobs",
                    "microsoft.com/careers",
                    "apple.com/careers",
                    "meta.com/careers",
                    "wellfound.com",
                    "stackoverflow.com/jobs",
                    "remoteco.com",
                    "weworkremotely.com",
                    "remoteok.com",
                    "flexjobs.com",
                    "naukri.com",
                    "seek.com.au",
                    "reed.co.uk",
                    "totaljobs.com"
                ]
            )
            
            return {
                "success": True,
                "jobs": results.get("results", []),
                "query": query,
                "location": location
            }
        except Exception as e:
            print(f"Tavily job search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "jobs": []
            }
    
    def format_job_result(self, result: Dict, index: int) -> str:
        """Format a single job search result for display"""
        title = result.get("title", "Job Listing")
        url = result.get("url", "")
        content = result.get("content", "No description available")
        
        # Clean up title - remove extra text after | or -
        if " | " in title:
            title = title.split(" | ")[0].strip()
        if " - " in title and len(title.split(" - ")[0]) > 10:
            parts = title.split(" - ")
            title = parts[0].strip()
        
        # Extract source from URL
        source = "Job Board"
        if "linkedin.com" in url:
            source = "LinkedIn"
        elif "indeed.com" in url:
            source = "Indeed"
        elif "glassdoor.com" in url:
            source = "Glassdoor"
        elif "monster.com" in url:
            source = "Monster"
        elif "ziprecruiter.com" in url:
            source = "ZipRecruiter"
        elif "dice.com" in url:
            source = "Dice"
        elif "google.com" in url:
            source = "Google Careers"
        elif "amazon.jobs" in url:
            source = "Amazon Jobs"
        elif "microsoft.com" in url:
            source = "Microsoft Careers"
        elif "apple.com" in url:
            source = "Apple Careers"
        elif "meta.com" in url:
            source = "Meta Careers"
        elif "wellfound.com" in url:
            source = "Wellfound"
        elif "naukri.com" in url:
            source = "Naukri"
        elif "seek.com" in url:
            source = "Seek"
        elif "reed.co.uk" in url:
            source = "Reed"
        elif "remote" in url.lower():
            source = "Remote Jobs"
        
        # Clean up content
        content = content.replace("\n", " ").replace("  ", " ").strip()
        if len(content) > 200:
            content = content[:200] + "..."
        
        formatted = f"""
### {index}. {title}

**Source:** {source}

{content}

[**Apply Now**]({url})

---
"""
        return formatted
    
    async def search_and_format(self, query: str, location: str = "") -> str:
        """Search for jobs and return formatted results"""
        result = await self.search_jobs(query, location)
        
        if not result["success"]:
            return f"""❌ **Error searching for jobs:** {result.get('error', 'Unknown error')}

Please try again later or check if Tavily is properly configured."""
        
        if not result["jobs"]:
            return f"""## No Recent Vacancies Found

No active job vacancies matching **{query}**{f' in **{location}**' if location else ''} were found.

**Try:**
- Different keywords
- Broader location
- More general terms (e.g., "developer" instead of "senior python developer")
"""
        
        output = f"""## Job Search Results

**Search:** {query}
**Location:** {location if location else 'Worldwide'}
**Results:** {len(result['jobs'])} active positions

---
"""
        
        for i, job in enumerate(result["jobs"], 1):
            output += self.format_job_result(job, i)
        
        output += """
*Click "Apply Now" to open the job posting and apply directly.*
"""
        
        return output
    
    def _is_follow_up_question(self, message: str) -> bool:
        """Detect if the message is a follow-up question rather than a new search"""
        message_lower = message.lower().strip()
        
        # Follow-up indicators
        follow_up_patterns = [
            "tell me more", "more about", "explain", "what about",
            "which one", "first one", "second one", "third one",
            "compare", "difference", "better", "best",
            "salary", "pay", "remote", "benefits",
            "requirements", "qualifications", "skills needed",
            "how to apply", "application", "interview",
            "thank", "thanks", "ok", "okay", "got it",
            "yes", "no", "sure", "great",
            "can you", "could you", "please",
            "what is", "what are", "how is", "how are",
            "why", "when", "where",
            "the job", "this job", "that job", "these jobs",
            "any of", "all of", "some of"
        ]
        
        # Check if it looks like a follow-up
        for pattern in follow_up_patterns:
            if pattern in message_lower:
                return True
        
        # Very short messages are likely follow-ups
        if len(message_lower.split()) <= 3 and not any(word in message_lower for word in ["jobs", "search", "find", "looking for"]):
            return True
        
        return False
    
    async def search_stream(self, query: str, location: str = "", session_id: str = "default"):
        """Stream job search results with conversational history"""
        # Get conversation history
        history_messages = self.get_windowed_history(session_id)
        has_history = len(history_messages) > 0
        print(f"[Jobs Memory] Session: {session_id}, History: {len(history_messages)} messages")
        
        # Check if this is a follow-up question or a new search
        is_follow_up = has_history and self._is_follow_up_question(query)
        
        if is_follow_up and self.llm:
            # Use LLM to respond conversationally based on history
            yield "💬 Let me help you with that...\n\n"
            
            system_prompt = """You are a helpful job search assistant. You have access to the conversation history which includes previous job search results.

Based on the conversation history:
1. Answer the user's follow-up questions about the jobs that were previously shown
2. Provide helpful advice about applications, interviews, or career decisions
3. If the user wants to search for different jobs, tell them to specify what jobs they're looking for
4. Be conversational and helpful

Remember: You can see the previous job listings in the conversation history - use that information to answer questions about specific jobs, comparisons, recommendations, etc."""

            messages = [SystemMessage(content=system_prompt)]
            
            # Add conversation history
            for hist_msg in history_messages:
                messages.append(hist_msg)
            
            # Add current user message
            messages.append(HumanMessage(content=query))
            
            full_response = ""
            try:
                async for chunk in self.llm.astream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        full_response += chunk.content
                        yield chunk.content
                
                # Save context
                if full_response:
                    self.save_context(session_id, query, full_response)
            except Exception as e:
                print(f"LLM error in job search: {e}")
                yield f"\n\nSorry, I encountered an error. Please try again."
        else:
            # New search - do the actual job search
            yield "🔍 Searching for job listings...\n\n"
            
            # Get the formatted results
            result = await self.search_and_format(query, location)
            
            # Stream the result in chunks for better UX
            chunk_size = 100
            for i in range(0, len(result), chunk_size):
                yield result[i:i + chunk_size]
            
            # Save context for history
            self.save_context(session_id, f"Search for: {query}" + (f" in {location}" if location else ""), result)


# Create singleton instances
roadmap_agent = RoadmapAgent()
resources_agent = ResourcesAgent()
summarizer_agent = SummarizerAgent()
quiz_agent = QuizAgent()
math_solver_agent = MathSolverAgent()
job_search_agent = JobSearchAgent()
