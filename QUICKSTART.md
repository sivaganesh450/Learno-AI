# Quick Start Guide for Lerno

## 🚀 Run Backend Server

Open a terminal in the project root and run:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

## 🌐 Run Frontend Server

Open another terminal in the project root and run:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

## ✅ Test the Application

1. Open http://localhost:5173
2. Click "Register here" to create an account
3. Fill in your details and register
4. You'll be automatically logged in and redirected to the dashboard
5. Click "New Chat" or use the suggestion cards to start learning!

## 🎯 What Can You Do?

- Ask questions about any subject (Math, Science, etc.)
- Get explanations of complex concepts
- Receive study tips and strategies
- Practice problem-solving
- Save multiple conversations

## 🔧 Troubleshooting

**Backend won't start?**
- Make sure MongoDB connection is working
- Check that Python 3.10+ is installed
- Verify all packages are installed: `pip list`

**Frontend won't start?**
- Delete node_modules and run `npm install` again
- Check that Node.js 18+ is installed
- Clear browser cache

**Can't login?**
- Make sure backend is running first
- Check browser console for errors
- Verify MongoDB is accessible

## 📝 Default Configuration

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Database: MongoDB Atlas (configured in .env)

Enjoy learning with Lerno! 🎓
