# Lerno AI - Requirements Document

## 1. Introduction
Lerno is an intelligent, AI-powered learning platform designed to personalize education. It leverages advanced Large Language Models (LLMs) to generate study roadmaps, create quizzes, summarize documents, and aggregate learning resources.

## 2. Functional Requirements

### 2.1 User Management
- **Registration**: Users must be able to create an account using email and password.
- **Authentication**: Secure login using JWT (JSON Web Tokens).
- **Profile Management**: Users can view and manage their profile details.

### 2.2 AI Learning Roadmap
- **Roadmap Generation**: Users can input a topic, and the system generates a structured, week-by-week study plan.
- **Customization**: Roadmaps should adapt to the user's specific goals or difficulty levels.

### 2.3 Interactive Quiz System
- **Quiz Generation**: AI generates multiple-choice questions (MCQs) based on a topic or difficulty.
- **Real-time Evaluation**: Immediate feedback on answers (correct/incorrect) with explanations.
- **Score Tracking**: Persistent tracking of quiz scores and history.
- **Session Management**: Ability to pause and resume quiz sessions (state persistence).

### 2.4 Document Summarizer (Agentic RAG)
- **File Upload**: Support for uploading PDF, DOCX, and PPTX files.
- **Summarization**: Generate concise summaries of uploaded documents.
- **Q&A**: Users can ask natural language questions about the document content.
- **Context Awareness**: The system uses Retrieval Augmented Generation (RAG) to provide accurate answers based on the document.

### 2.5 Resource Aggregator
- **Content Search**: Find relevant external learning resources (videos, articles, courses).
- **Filtering**: Rank resources by relevance and quality.

### 2.6 Math Solver (Visual Reasoning)
- **Problem Solving**: Accept text or image inputs of math problems.
- **Step-by-Step Solutions**: Provide detailed, logical steps to reach the solution.

### 2.7 Job Search Agent
- **Opportunity Finding**: Search for job listings based on user skills and preferences.

## 3. Non-Functional Requirements

### 3.1 Performance
- **Response Time**: AI responses should be streamed where possible to reduce perceived latency.
- **Concurrency**: The system manages multiple concurrent user sessions efficiently.

### 3.2 Security
- **Data Protection**: User passwords must be hashed (Argon2).
- **Communication**: All data transmission must occur over HTTPS.
- **Access Control**: API endpoints are protected via JWT authentication.

### 3.3 Reliability & Availability
- **Error Handling**: Graceful handling of AI model failures, API rate limits, or network issues.
- **Uptime**: Designed for 24/7 availability on cloud platforms (Render/Vercel).

### 3.4 Scalability
- **Architecture**: Stateless backend design allows for horizontal scaling.
- **Database**: MongoDB handles flexible and growing data schemas effectively.

### 3.5 Usability
- **Interface**: Clean, responsive, and intuitive UI (React + Glassmorphism).
- **Feedback**: Clear visual feedback for system actions (loading states, success/error toasts).
