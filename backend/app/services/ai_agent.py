import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage

# Initialize Bedrock LLM (Llama 3.3 70B)
llm = ChatBedrockConverse(
    model=os.getenv('BEDROCK_MODEL_ID', 'us.meta.llama3-3-70b-instruct-v1:0'),
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    max_tokens=2048,
    temperature=0.7,
)


class LearningAgent:
    """
    AI Agent for student learning assistance
    Uses Amazon Bedrock (Llama 3.3 70B) for intelligent tutoring
    """
    
    def __init__(self):
        self.llm = llm
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
        Generate an AI response using Amazon Bedrock (Claude 3 Haiku)
        
        Args:
            message: The student's current message
            conversation_history: Previous messages in the conversation
            subject: Optional subject context (e.g., "Math", "Science")
        
        Returns:
            AI-generated response
        """
        if not self.llm:
            return "Error: AI model not initialized. Please check Bedrock configuration."

        context = f"\nSubject context: {subject}" if subject else ""
        history_text = self._build_conversation_context(conversation_history)
        
        user_prompt = f"""Conversation History:
{history_text}

Current Question: {message}{context}

Provide a helpful, educational response."""

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = await self.llm.ainvoke(messages)
            content = response.content
            # Handle list content from ChatBedrockConverse (Llama 3.3)
            if isinstance(content, list):
                content = "".join(
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in content
                )
            return content
        except Exception as e:
            print(f"Bedrock LLM error: {e}")
            return f"I'm sorry, I encountered an error generating a response. Please try again. Error: {str(e)}"

    def _build_conversation_context(self, history: List[Dict[str, str]]) -> str:
        """Build context from conversation history"""
        context = []
        for msg in history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "")
            content = msg.get("content", "")
            context.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(context) if context else "No previous conversation."

learning_agent = LearningAgent()
