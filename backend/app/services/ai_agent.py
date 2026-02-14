import json
from typing import List, Dict, Optional
from datetime import datetime

class LearningAgent:
    """
    AI Agent for student learning assistance
    Provides intelligent tutoring, explanations, and learning support
    """
    
    def __init__(self):
        self.system_prompt = """You are Lerno, an intelligent AI learning assistant designed to help students learn effectively. Your role is to:

1. Explain concepts clearly and adapt to the student's level
2. Break down complex topics into manageable parts
3. Provide examples and analogies to aid understanding
4. Ask clarifying questions to assess comprehension
5. Encourage critical thinking and problem-solving
6. Offer study tips and learning strategies
7. Be patient, supportive, and encouraging

Always maintain a friendly, educational tone and tailor your explanations to the student's needs."""
    
    async def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        subject: Optional[str] = None
    ) -> str:
        """
        Generate an AI response based on the student's message
        
        Args:
            message: The student's current message
            conversation_history: Previous messages in the conversation
            subject: Optional subject context (e.g., "Math", "Science")
        
        Returns:
            AI-generated response
        """
        
        # For demonstration purposes, this is a rule-based response
        # In production, integrate with OpenAI, Anthropic, or other LLM APIs
        
        context = f"\nSubject: {subject}" if subject else ""
        
        # Simple rule-based responses for demo
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm Lerno, your AI learning assistant. How can I help you with your studies today?{context}"
        
        elif any(word in message_lower for word in ["explain", "what is", "what are"]):
            return f"""I'd be happy to explain that! Let me break it down for you:

To give you the best explanation, could you tell me:
1. What specific concept would you like me to explain?
2. What level are you studying at (high school, college, etc.)?
3. Are there any particular aspects you find confusing?

This will help me tailor my explanation to your needs.{context}"""
        
        elif any(word in message_lower for word in ["help", "stuck", "don't understand"]):
            return """I'm here to help! When you're stuck, let's work through it together:

1. **Identify the specific problem**: What exactly are you finding difficult?
2. **Review what you know**: What parts do you already understand?
3. **Break it down**: Let's tackle one piece at a time
4. **Practice**: Apply the concept with examples

Tell me more about what you're working on, and I'll guide you step by step!"""
        
        elif any(word in message_lower for word in ["study tips", "how to study"]):
            return """Great question! Here are some effective study strategies:

📚 **Active Learning**
- Teach the concept to someone else
- Create mind maps or diagrams
- Practice with real problems

⏰ **Time Management**
- Use the Pomodoro Technique (25 min focus, 5 min break)
- Study in shorter, focused sessions
- Review material regularly (spaced repetition)

🎯 **Stay Organized**
- Keep notes organized by subject
- Set specific learning goals
- Track your progress

💡 **Optimize Your Environment**
- Find a quiet, comfortable study space
- Minimize distractions
- Stay hydrated and take breaks

What subject are you studying? I can provide more specific tips!"""
        
        elif any(word in message_lower for word in ["math", "mathematics", "calculate", "solve"]):
            return """I can help with math! I'm great at:

📐 **Topics I cover:**
- Algebra and equations
- Geometry and trigonometry
- Calculus and derivatives
- Statistics and probability
- Word problems and applications

To help you effectively, please share:
1. The specific problem or topic
2. What you've tried so far
3. Where you're getting stuck

Let's solve this together! What's your math question?"""
        
        elif any(word in message_lower for word in ["science", "physics", "chemistry", "biology"]):
            return """Science is fascinating! I can assist with:

🔬 **Scientific Topics:**
- Physics: mechanics, energy, electricity
- Chemistry: reactions, elements, molecules
- Biology: cells, genetics, ecosystems
- Scientific method and experiments

What science topic are you studying? Share your question, and I'll help you understand the concepts clearly!"""
        
        else:
            # Generic helpful response
            return f"""I'm here to help you learn! I can assist with:

✓ Explaining difficult concepts
✓ Solving problems step-by-step
✓ Providing study strategies
✓ Answering subject-specific questions
✓ Reviewing and practicing material

Could you tell me more about what you'd like help with? The more specific you are, the better I can assist you!{context}"""
    
    def _build_conversation_context(self, history: List[Dict[str, str]]) -> str:
        """Build context from conversation history"""
        context = []
        for msg in history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "")
            content = msg.get("content", "")
            context.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(context)

learning_agent = LearningAgent()
