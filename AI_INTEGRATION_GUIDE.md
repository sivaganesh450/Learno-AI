# Integrating Real AI Models (OpenAI or Anthropic)

The current implementation uses a rule-based AI agent. To integrate real AI models like OpenAI's GPT or Anthropic's Claude, follow these instructions.

## Option 1: OpenAI Integration

### 1. Install OpenAI SDK
Already included in requirements.txt, but verify:
```bash
pip install openai
```

### 2. Add API Key to .env
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Update ai_agent.py

Replace the `generate_response` method in `backend/app/services/ai_agent.py`:

```python
from openai import AsyncOpenAI
from app.core.config import settings

class LearningAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.system_prompt = """You are Lerno, an intelligent AI learning assistant..."""
    
    async def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        subject: Optional[str] = None
    ) -> str:
        if not self.client:
            return "AI service not configured. Please add OPENAI_API_KEY to .env"
        
        try:
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # or "gpt-3.5-turbo" for cheaper option
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
```

## Option 2: Anthropic Claude Integration

### 1. Install Anthropic SDK
Already included in requirements.txt, but verify:
```bash
pip install anthropic
```

### 2. Add API Key to .env
```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### 3. Update ai_agent.py

Replace the `generate_response` method:

```python
from anthropic import AsyncAnthropic
from app.core.config import settings

class LearningAgent:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.system_prompt = """You are Lerno, an intelligent AI learning assistant..."""
    
    async def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        subject: Optional[str] = None
    ) -> str:
        if not self.client:
            return "AI service not configured. Please add ANTHROPIC_API_KEY to .env"
        
        try:
            # Build messages for Claude
            messages = []
            
            # Add conversation history
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call Anthropic API
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # or other Claude models
                max_tokens=1000,
                system=self.system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
```

## Option 3: LangChain Integration (Recommended for Advanced Features)

LangChain is already in requirements.txt. It provides a unified interface for multiple AI providers:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.core.config import settings

class LearningAgent:
    def __init__(self):
        # Choose your provider
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model="gpt-4o",
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )
        elif settings.ANTHROPIC_API_KEY:
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.7
            )
        else:
            self.llm = None
        
        self.system_prompt = """You are Lerno, an intelligent AI learning assistant..."""
    
    async def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        subject: Optional[str] = None
    ) -> str:
        if not self.llm:
            return "AI service not configured. Please add API key to .env"
        
        try:
            # Build messages
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add conversation history
            for msg in conversation_history[-10:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Get response
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
```

## Getting API Keys

### OpenAI
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Add billing information (pay-as-you-go)

### Anthropic
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Add billing information

## Cost Considerations

### OpenAI Pricing (as of 2024)
- GPT-4o: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens
- GPT-3.5-turbo: ~$0.50 per 1M input tokens, ~$1.50 per 1M output tokens

### Anthropic Pricing
- Claude 3.5 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Claude 3 Haiku: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens

### Tips to Reduce Costs
1. Use GPT-3.5-turbo or Claude Haiku for lower costs
2. Limit conversation history to last 5-10 messages
3. Set max_tokens to control response length
4. Implement rate limiting
5. Cache common responses

## Advanced Features You Can Add

1. **RAG (Retrieval Augmented Generation)**
   - Upload study materials
   - Search through textbooks
   - Cite sources

2. **Function Calling**
   - Calculator for math
   - Code execution
   - Web search

3. **Streaming Responses**
   - Real-time token streaming
   - Better user experience

4. **Multi-modal Support**
   - Image recognition (diagrams, equations)
   - Document analysis

## Testing

After integration, test with:
```bash
# Backend must be running
curl -X POST "http://localhost:8000/api/v1/chat/send" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain photosynthesis"}'
```

## Security Notes

- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor usage and set spending limits
- Implement rate limiting in production

## Support

For more details:
- OpenAI Docs: https://platform.openai.com/docs
- Anthropic Docs: https://docs.anthropic.com/
- LangChain Docs: https://python.langchain.com/
