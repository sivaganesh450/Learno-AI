# Lerno — Agentic AI Student Learning Assistant

Lerno is a full-stack AI-powered learning platform built with **FastAPI** and **React 19**, deployed on **AWS**. It combines conversational AI, autonomous learning agents, Retrieval-Augmented Generation (RAG), OCR, and live web search to give students a powerful, context-aware study companion.

## 🌐 Live Deployment

| Component | URL |
|---|---|
| **Frontend** | https://d8y63sf81k9rq.cloudfront.net |
| **Backend API** | https://ih2ztarjgh.execute-api.us-east-1.amazonaws.com/demo |
| **API Health Check** | https://ih2ztarjgh.execute-api.us-east-1.amazonaws.com/demo/health |

---

## ✨ Features

| Category | Details |
|---|---|
| **Agentic AI** | LangGraph-powered agents that plan, reason, and use tools autonomously |
| **RAG** | Upload documents (PDF, DOCX) — the agent searches your own material |
| **Web Search** | Tavily integration lets the agent retrieve up-to-date information from the web |
| **OCR** | Extract and query text from images using Amazon Textract |
| **Amazon Bedrock** | Powered by Claude 3 Haiku via `langchain-aws` |
| **Math & Science** | SymPy-backed symbolic math solver |
| **Auth** | Secure JWT authentication with bcrypt password hashing |
| **Conversations** | Persistent chat history stored in MongoDB Atlas |
| **Agent Sessions** | Separate agent-chat sessions with full message history |
| **Responsive UI** | React 19 frontend with a clean Blue / Black / White theme |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI 0.115** — async REST API with auto-generated Swagger docs
- **Mangum 0.17** — AWS Lambda adapter for ASGI apps
- **MongoDB Atlas + Motor** — async NoSQL database
- **LangGraph ≥ 0.2** — agentic workflow orchestration
- **LangChain AWS ≥ 0.2** — Amazon Bedrock (Claude 3 Haiku) integration
- **Amazon Textract** — OCR for image-based documents
- **Amazon S3** — file uploads and static hosting
- **Tavily Python 0.7** — real-time web search tool
- **PyPDF + python-docx** — PDF and Word document parsing
- **SymPy + NumPy** — symbolic and numeric math
- **Pydantic v2 + pydantic-settings** — data validation & config
- **python-jose + passlib** — JWT auth & password security

### Frontend
- **React 19** — latest React with concurrent features
- **Vite 7** — fast dev server and build tool
- **React Router v6** — client-side routing
- **Axios** — API client

### AWS Infrastructure
- **AWS Lambda** — serverless backend (Python 3.12, 1024 MB, 300s timeout)
- **API Gateway** — REST API with `{proxy+}` Lambda integration
- **Amazon S3** — frontend static hosting + file uploads
- **Amazon CloudFront** — CDN for frontend distribution
- **Amazon Bedrock** — Claude 3 Haiku LLM
- **Amazon Textract** — OCR text extraction

---

## 📁 Project Structure

```
Lerno/
├── backend/
│   ├── main.py                         # FastAPI app + Mangum Lambda handler
│   ├── requirements.txt
│   ├── Dockerfile                      # Lambda container (optional)
│   ├── lambda-trust-policy.json        # IAM trust policy
│   ├── cloudfront-config.json          # CloudFront distribution config
│   └── app/
│       ├── api/v1/
│       │   ├── api.py                  # Router aggregation
│       │   ├── deps.py                 # Shared dependencies
│       │   └── endpoints/
│       │       ├── auth.py             # Register / login
│       │       ├── users.py            # User profile
│       │       ├── chat.py             # Standard conversations
│       │       ├── agents.py           # Agent management
│       │       └── agent_chats.py      # Agent chat sessions
│       ├── core/
│       │   ├── config.py               # App settings (env vars)
│       │   ├── database.py             # MongoDB connection
│       │   └── security.py             # JWT & bcrypt helpers
│       ├── models/
│       │   ├── user.py
│       │   ├── conversation.py
│       │   └── agent_chat.py
│       └── services/
│           ├── ai_agent.py             # Bedrock Claude agent logic
│           ├── agents.py               # LangGraph agent workflows
│           ├── agent_chat_service.py   # Agent session management
│           ├── rag_service.py          # RAG pipeline (Bedrock + Textract)
│           ├── ocr_service.py          # Amazon Textract OCR
│           ├── conversation_service.py
│           └── user_service.py
│
└── frontend/
    ├── .env.development                # Local API URL
    ├── .env.production                 # AWS API Gateway URL
    └── src/
        ├── App.jsx
        ├── context/
        │   └── AuthContext.jsx
        ├── components/
        │   ├── PrivateRoute.jsx
        │   └── ChatSidebar.jsx
        ├── pages/
        │   ├── Login.jsx
        │   ├── Register.jsx
        │   ├── Dashboard.jsx           # Standard chat dashboard
        │   └── AgentChat.jsx           # Agentic AI chat interface
        └── services/
            ├── api.js
            ├── authService.js
            └── agentService.js
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB Atlas account
- AWS account with Bedrock access (Claude 3 Haiku enabled in us-east-1)
- AWS CLI v2 configured
- Tavily API key (for web search)

### Local Development

#### Backend Setup

1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the `backend/` directory:
   ```env
   MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=lerno
   DATABASE_NAME=lerno_db
   SECRET_KEY=your-secret-key-here
   TAVILY_API_KEY=your-tavily-api-key
   AWS_REGION=us-east-1
   S3_UPLOADS_BUCKET=lerno-uploads-demo
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
   ```

5. **Start the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   | URL | Description |
   |---|---|
   | `http://localhost:8000` | Base API |
   | `http://localhost:8000/docs` | Swagger UI |
   | `http://localhost:8000/redoc` | ReDoc |

#### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   Frontend available at: `http://localhost:5173`

---

## 🎮 Usage

1. **Register** — create a free account at https://d8y63sf81k9rq.cloudfront.net/register (or `http://localhost:5173/register` for local dev)
2. **Log in** — authenticate with your credentials
3. **Standard Chat** — open the Dashboard and start a general Q&A conversation
4. **Agent Chat** — navigate to an agent session for autonomous, tool-using AI:
   - Upload PDFs or DOCX files for RAG-powered document Q&A
   - Ask questions that require live web search
   - Upload images to extract text via Amazon Textract OCR
   - Solve math/science problems with symbolic computation

---

## 📚 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Obtain a JWT token |

### Users
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/users/me` | Get current user profile |

### Conversations
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat/send` | Send message to AI |
| `GET` | `/api/v1/chat/conversations` | List all conversations |
| `GET` | `/api/v1/chat/conversations/{id}` | Get a conversation |
| `DELETE` | `/api/v1/chat/conversations/{id}` | Delete a conversation |

### Agents
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/agents` | List available agents |
| `POST` | `/api/v1/agents` | Create a new agent |

### Agent Chats
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/agent-chats/send` | Send message to an agent |
| `GET` | `/api/v1/agent-chats` | List agent chat sessions |
| `GET` | `/api/v1/agent-chats/{id}` | Get a session |
| `DELETE` | `/api/v1/agent-chats/{id}` | Delete a session |

---

## 🤖 Agentic AI Capabilities

Lerno's LangGraph-powered agents can:

- 📄 **RAG over your documents** — chunk, embed, and retrieve from uploaded PDFs and Word files
- 🌐 **Live web search** — pull current information via Tavily when training data is insufficient
- 🖼️ **OCR** — extract and reason over text from scanned images using Amazon Textract
- 🧮 **Symbolic math** — solve equations and simplify expressions with SymPy
- 💬 **Multi-turn reasoning** — maintain context across long conversations powered by Claude 3 Haiku
- 🔍 **Step-by-step explanations** — break down complex topics for students

---

## 🔒 Security

- JWT-based authentication with configurable expiry
- bcrypt password hashing
- CORS configuration for frontend/backend separation
- All secrets managed via environment variables — never hardcoded

---

## 🎨 UI Color Theme

| Token | Value |
|---|---|
| Primary Blue | `#1e88e5` |
| Dark Blue | `#0d47a1` |
| Light Blue | `#64b5f6` |
| Black | `#000000` |
| White | `#ffffff` |

---

## 🔄 Roadmap

- [ ] Voice input / text-to-speech output
- [ ] Progress tracking and learning analytics dashboard
- [ ] Multi-language support
- [ ] Collaborative study rooms
- [ ] Assignment and deadline management
- [ ] Calendar integration

---

## 🐛 Troubleshooting

### Backend (Local)
- **MongoDB connection error** — verify `MONGO_URI` in `.env` and that your IP is whitelisted in Atlas
- **Bedrock API error** — confirm your AWS credentials have Bedrock access and Claude 3 Haiku is enabled in `us-east-1`
- **Dependency issues** — `pip install -r requirements.txt` inside an activated virtualenv

### Backend (AWS Lambda)
- **Internal Server Error** — check CloudWatch logs at `/aws/lambda/lerno-backend`
- **Missing module errors** — ensure all dependencies are in the Lambda zip (keep `.dist-info` directories)
- **Timeout** — Lambda timeout is 300s; increase if agents need more time

### Frontend
- **Blank page / routing errors** — clear browser cache, confirm `npm install` completed
- **API calls failing (CORS)** — ensure the CloudFront URL is in the Lambda CORS `allow_origins` list
- **Wrong API URL** — check `.env.production` has the correct API Gateway URL
- **Package issues** — delete `node_modules/` and `package-lock.json`, then run `npm install`

---

## 🚢 AWS Deployment

The project is fully deployed on AWS using a serverless architecture:

### Architecture
```
CloudFront (CDN) → S3 (Frontend)
API Gateway (REST) → Lambda (FastAPI + Mangum)
                       ├── Amazon Bedrock (Claude 3 Haiku)
                       ├── Amazon Textract (OCR)
                       ├── Amazon S3 (File uploads)
                       └── MongoDB Atlas (Database)
```

### AWS Resources
| Resource | Name / ID | Details |
|---|---|---|
| **Lambda** | `lerno-backend` | Python 3.12, 1024 MB, 300s timeout |
| **API Gateway** | `ih2ztarjgh` | REST API, stage: `demo` |
| **S3 (Frontend)** | `lerno-frontend-demo` | Static website hosting |
| **S3 (Uploads)** | `lerno-uploads-demo` | File uploads + Lambda zip |
| **CloudFront** | `E3ENBK1TY2ST0R` | OAC to S3, 403→index.html fallback |
| **IAM Role** | `AmazonBedrockLambdaExecutionRole-*` | Lambda + CloudWatch + Bedrock |

### Redeploying

**Backend:**
```bash
cd backend
# Rebuild the Lambda zip (see lambda_package/ directory)
aws s3 cp lambda_deployment.zip s3://lerno-uploads-demo/lambda/lambda_deployment.zip
aws lambda update-function-code --function-name lerno-backend \
  --s3-bucket lerno-uploads-demo --s3-key lambda/lambda_deployment.zip
```

**Frontend:**
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://lerno-frontend-demo --delete
aws cloudfront create-invalidation --distribution-id E3ENBK1TY2ST0R --paths "/*"
```

### Lambda Environment Variables
| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB Atlas connection string |
| `DATABASE_NAME` | Database name (`lerno_db`) |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | JWT algorithm (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL in minutes |
| `TAVILY_API_KEY` | Tavily web search API key |
| `S3_UPLOADS_BUCKET` | S3 bucket for uploads |
| `BEDROCK_MODEL_ID` | Bedrock model ID |

---

## 📝 License

This project is created for educational purposes.

## 👥 Contributing

Contributions are welcome! Please open a Pull Request with a clear description of your changes.

## 📧 Support

Open an issue in the repository for bugs or feature requests.

---

**Built with ❤️ for students everywhere**
