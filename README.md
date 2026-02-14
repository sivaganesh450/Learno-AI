# Lerno - AI-Powered Student Learning Assistant

Lerno is a modern, intelligent learning platform that helps students study effectively using advanced AI providers (Google Gemini 1.5 Flash). It offers personalized roadmaps, interactive quizzes, resource gathering, and document summarization.

## 🚀 Features

*   **🎓 AI Learning Roadmap**: Generates personalized week-by-week study plans for any topic.
*   **🧠 Intelligent Quiz System**: Interactive quizzes with persistent score tracking and detailed feedback.
*   **📚 Resource Aggregator**: Finds the best videos, articles, and courses for your subjects.
*   **📄 Document Summarizer (RAG)**: Upload **PDFs, DOCX, and PPTX** files to get summaries and ask questions.
*   **🧮 Math Solver**: Step-by-step solutions for math problems using visual reasoning.
*   **💼 Job Search Agent**: AI-powered assistant to find relevant job opportunities.
*   **Testing & Interviews**: Mock interview preparation with real-time feedback.

## �️ Tech Stack

### Backend
*   **Framework**: FastAPI (Python 3.11+)
*   **Database**: MongoDB (Motor async driver)
*   **AI Engine**: Google Gemini 1.5 Flash (via `google-genai` SDK)
*   **Vector DB**: ChromaDB (for RAG retrieval)
*   **Authentication**: JWT + Argon2 (Secure password hashing)
*   **File Processing**: `pypdf`, `python-docx`, `python-pptx` (for RAG)

### Frontend
*   **Framework**: React 19 + Vite
*   **Styling**: Modern CSS3 (Glassmorphism, Dark/Light modes)
*   **State Management**: React Context API
*   **Routing**: React Router

## ⚡ Getting Started

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   MongoDB Atlas Account
*   Google AI Studio API Key (Gemini)

### Backend Setup

1.  **Clone the repository and navigate to backend:**
    ```bash
    cd backend
    ```

2.  **Create and activate virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables (.env):**
    Create a `.env` file in the `backend/` directory:
    ```env
    MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/lerno_db
    DB_NAME=lerno_db
    SECRET_KEY=your_super_secret_key_here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=1440
    GOOGLE_API_KEY=your_gemini_api_key_here
    # Optional: Tavily API for web search
    # TAVILY_API_KEY=tvly-...
    ```

5.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    Backend will run at: `http://localhost:8000`

### Frontend Setup

1.  **Navigate to frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Environment Variables (.env):**
    Create a `.env` file in the `frontend/` directory (or use `.env.local`):
    ```env
    VITE_API_URL=http://localhost:8000/api/v1
    ```

4.  **Run the development server:**
    ```bash
    npm run dev
    ```
    Frontend will run at: `http://localhost:5173`

## 🌍 Deployment

### Backend (Render)
1.  Connect your repo to **Render**.
2.  Select **Web Service**.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `./start.sh` (or `uvicorn app.main:app --host 0.0.0.0 --port 10000`)
5.  **Environment Variables**: Add `MONGO_URI`, `GOOGLE_API_KEY`, etc.
6.  **Python Version**: Ensure specific version (e.g., 3.11.9) if needed via `render.yaml` (optional).

### Frontend (Vercel)
1.  Connect your repo to **Vercel**.
2.  Select `Vite` framework preset.
3.  Add Environment Variable `VITE_API_URL` pointing to your Render Backend URL (e.g., `https://lerno-backend.onrender.com/api/v1`).
4.  Deploy!

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## � License
This project is open-source and available under the MIT License.
