# Lerno - Student Learning Assistant with Agentic AI

A modern web-based AI-powered learning assistant built with FastAPI and React. Lerno helps students learn effectively through intelligent tutoring, explanations, and personalized learning support.

## 🎯 Features

- **AI-Powered Learning Assistant**: Intelligent chatbot that helps with studying, problem-solving, and concept explanations
- **User Authentication**: Secure JWT-based student/user authentication
- **Conversation Management**: Save and manage multiple learning conversations
- **Real-time Chat Interface**: Interactive messaging with the AI learning agent
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Clean interface with Blue, Black, and White color theme

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database with Motor (async driver)
- **JWT Authentication**: Secure token-based authentication
- **Python 3.10+**: Latest Python features
- **Pydantic**: Data validation and settings management

### Frontend
- **React 19**: Latest React features
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **CSS3**: Custom styling with CSS variables

## 📁 Project Structure

```
Lerno/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py         # Authentication endpoints
│   │   │       │   ├── chat.py         # Chat/conversation endpoints
│   │   │       │   └── users.py        # User management endpoints
│   │   │       ├── api.py              # API router
│   │   │       └── deps.py             # Dependencies
│   │   ├── core/
│   │   │   ├── config.py               # Configuration settings
│   │   │   ├── database.py             # MongoDB connection
│   │   │   └── security.py             # JWT and password handling
│   │   ├── models/
│   │   │   ├── user.py                 # User models
│   │   │   └── conversation.py         # Conversation models
│   │   └── services/
│   │       ├── user_service.py         # User business logic
│   │       ├── conversation_service.py # Conversation management
│   │       └── ai_agent.py             # AI learning agent
│   ├── main.py                         # FastAPI application entry
│   ├── requirements.txt                # Python dependencies
│   └── .env                            # Environment variables
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── PrivateRoute.jsx        # Protected route component
    │   ├── context/
    │   │   └── AuthContext.jsx         # Authentication context
    │   ├── pages/
    │   │   ├── Login.jsx               # Login page
    │   │   ├── Register.jsx            # Registration page
    │   │   └── Dashboard.jsx           # Main chat dashboard
    │   ├── services/
    │   │   ├── api.js                  # Axios configuration
    │   │   └── authService.js          # API service functions
    │   ├── App.jsx                     # Main App component
    │   ├── main.jsx                    # React entry point
    │   └── index.css                   # Global styles
    ├── index.html
    ├── package.json
    └── vite.config.js

```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- MongoDB Atlas account (or local MongoDB)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - The `.env` file is already configured with your MongoDB connection
   - Update `SECRET_KEY` for production use

5. **Run the backend server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend API will be available at: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at: `http://localhost:5173`

## 🎮 Usage

1. **Register a new account**
   - Navigate to `http://localhost:5173`
   - Click "Register here" and create your account

2. **Login**
   - Use your credentials to log in

3. **Start learning**
   - Click "New Chat" to start a conversation
   - Ask questions about any subject
   - The AI will help you understand concepts, solve problems, and improve your learning

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

### Users
- `GET /api/v1/users/me` - Get current user info

### Chat
- `POST /api/v1/chat/send` - Send message to AI
- `GET /api/v1/chat/conversations` - Get all conversations
- `GET /api/v1/chat/conversations/{id}` - Get specific conversation
- `DELETE /api/v1/chat/conversations/{id}` - Delete conversation

## 🤖 AI Agent Features

The learning agent can help with:

- **Concept Explanations**: Clear explanations of complex topics
- **Problem Solving**: Step-by-step guidance through problems
- **Study Strategies**: Tips and techniques for effective learning
- **Subject Support**: Math, Science, and other academic subjects
- **Interactive Learning**: Questions and clarifications

## 🔒 Security

- JWT token-based authentication
- Password hashing with bcrypt
- Secure HTTP-only token storage
- CORS protection
- Environment-based configuration

## 🎨 Color Theme

The application uses a professional Blue, Black, and White color scheme:

- **Primary Blue**: `#1e88e5`
- **Dark Blue**: `#0d47a1`
- **Light Blue**: `#64b5f6`
- **Black**: `#000000`
- **White**: `#ffffff`

## 🔄 Future Enhancements

- [ ] Integration with OpenAI GPT-4 or Anthropic Claude
- [ ] File upload for homework help
- [ ] Voice input/output
- [ ] Progress tracking and analytics
- [ ] Multiple language support
- [ ] Collaborative learning features
- [ ] Assignment management
- [ ] Calendar integration

## 🐛 Troubleshooting

### Backend Issues
- Ensure MongoDB is accessible
- Check Python version: `python --version`
- Verify all dependencies are installed: `pip list`

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version`
- Clear browser cache

### CORS Issues
- Ensure backend CORS settings include frontend URL
- Check that both servers are running

## 📝 License

This project is created for educational purposes.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue in the repository.

---

**Built with ❤️ for students everywhere**
