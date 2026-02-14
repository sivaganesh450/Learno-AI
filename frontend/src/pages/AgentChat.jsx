import { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { agentService } from '../services/agentService';
import ChatSidebar from '../components/ChatSidebar';
import './AgentChat.css';

const agentConfig = {
  roadmap: {
    name: 'Roadmap Generator',
    icon: '🗺️',
    color: '#1e88e5',
    description: 'Create personalized learning paths tailored to your goals',
    placeholder: 'Ask follow-up questions about your roadmap...',
    welcomeMessage: "Hello! I'm your Roadmap Generator. Please fill out the form below to help me create a personalized learning path for you."
  },
  resources: {
    name: 'Resources Provider',
    icon: '📚',
    color: '#0d47a1',
    description: 'Access curated learning materials and resources',
    placeholder: 'What topic do you need resources for? (e.g., "JavaScript tutorials for beginners")',
    welcomeMessage: "Hi there! I'm your Resources Provider. I can help you find the best learning materials including courses, tutorials, books, and practice exercises. What would you like to learn?"
  },
  qa: {
    name: 'Summarizer',
    icon: '�',
    color: '#64b5f6',
    description: 'Upload documents and get AI-powered answers',
    placeholder: 'Ask any question about your uploaded documents...',
    welcomeMessage: "Welcome! I'm your Summarizer Assistant."
  },
  quiz: {
    name: 'Question Answering System',
    icon: '❓',
    color: '#ff9800',
    description: 'Interactive Q&A for interview prep, exam, and knowledge testing',
    placeholder: 'Type your answer or use commands: start, next, score, end',
    welcomeMessage: "Welcome to the Question Answering System! 🎯\n\nI'll help you prepare for interviews, exams, or test your knowledge. Please fill out the form below to customize your session."
  },
  math: {
    name: 'Problem Solver',
    icon: '🧮',
    color: '#9c27b0',
    description: 'Solve complex math problems with step-by-step Chain of Thought reasoning',
    placeholder: 'Enter a math problem (e.g., "Solve x² + 5x + 6 = 0" or "Find the derivative of x³ + 2x²")',
    welcomeMessage: "Welcome to the Problem Solver! 🧮\n\nI use **Chain of Thought (CoT)** reasoning to solve complex math problems step-by-step.\n\n**Supported topics:**\n- 📐 Algebra (equations, factoring, simplification)\n- 📈 Calculus (derivatives, integrals, limits)\n- 🔺 Geometry (area, volume, angles)\n- 📊 Trigonometry (sin, cos, tan)\n- 📉 Statistics (mean, median, probability)\n- ➗ Linear Algebra (matrices, vectors)\n\nType your math problem and I'll solve it with detailed explanations!"
  },
  jobs: {
    name: 'Job Search',
    icon: '💼',
    color: '#4caf50',
    description: 'Search for recent job listings worldwide',
    placeholder: 'Search jobs (e.g., "python developer in London" or "data scientist in New York")',
    welcomeMessage: "Welcome to Job Search! 💼\n\nI'll help you find recent job listings from around the world using Adzuna.\n\n**How to search:**\n- Type a job title: `software engineer`\n- Add location: `software engineer in London`\n- Specify country: `data analyst in Sydney, Australia`\n\n**Supported countries:**\n🇬🇧 UK | 🇺🇸 USA | 🇦🇺 Australia | 🇨🇦 Canada | 🇩🇪 Germany | 🇫🇷 France | 🇮🇳 India | 🇸🇬 Singapore | and more!\n\nStart by typing a job title or role you're looking for!"
  }
};

function AgentChat() {
  const { agentId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const mathImageInputRef = useRef(null);

  // Chat persistence state
  const [currentChatId, setCurrentChatId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loadingChat, setLoadingChat] = useState(false);

  // Roadmap questionnaire state
  const [showRoadmapForm, setShowRoadmapForm] = useState(true);
  const [roadmapGenerated, setRoadmapGenerated] = useState(false);
  const [roadmapForm, setRoadmapForm] = useState({
    domain: '',
    skillsKnown: '',
    level: 'beginner',
    duration: '3 months'
  });

  // Summarizer RAG state
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  // Math solver image upload state
  const [isUploadingMathImage, setIsUploadingMathImage] = useState(false);

  // Quiz agent state
  const [showQuizForm, setShowQuizForm] = useState(true);
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizForm, setQuizForm] = useState({
    domain: '',
    purpose: 'interview',
    difficulty: 'moderate'
  });

  const agent = agentConfig[agentId];

  // Load chat from URL param or start fresh
  const loadChatFromId = useCallback(async (chatId) => {
    if (!chatId) return false;
    
    setLoadingChat(true);
    try {
      const chat = await agentService.getChat(chatId);
      if (chat && chat.agent_type === agentId) {
        setCurrentChatId(chatId);
        // Convert chat messages to display format
        const displayMessages = chat.messages.map((msg, idx) => ({
          id: idx + 1,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(displayMessages.length > 0 ? displayMessages : [{
          id: 1,
          role: 'assistant',
          content: agent.welcomeMessage,
          timestamp: new Date()
        }]);
        setShowRoadmapForm(false);
        setShowQuizForm(false);
        setRoadmapGenerated(agentId === 'roadmap' && displayMessages.length > 1);
        setQuizStarted(agentId === 'quiz' && displayMessages.length > 1);
        setLoadingChat(false);
        return true;
      } else {
        // Chat doesn't match this agent - clear URL and start fresh
        console.log('Chat agent_type mismatch, starting fresh');
        setLoadingChat(false);
        return false;
      }
    } catch (error) {
      console.error('Failed to load chat:', error);
    }
    setLoadingChat(false);
    return false;
  }, [agentId, agent]);

  // Reset state when agent changes
  useEffect(() => {
    if (!agent) {
      navigate('/dashboard');
      return;
    }
    
    // Clear chat state when switching agents
    setCurrentChatId(null);
    
    // Check for chat_id in URL
    const chatIdFromUrl = searchParams.get('chat');
    if (chatIdFromUrl) {
      // Async load - if it fails or doesn't match, start fresh
      loadChatFromId(chatIdFromUrl).then(loaded => {
        if (!loaded) {
          // Clear the invalid chat param and start fresh
          setSearchParams({}, { replace: true });
          startFreshChat();
        }
      });
    } else {
      startFreshChat();
    }
    
    function startFreshChat() {
      setCurrentChatId(null);
      setMessages([
        {
          id: 1,
          role: 'assistant',
          content: agent.welcomeMessage,
          timestamp: new Date()
        }
      ]);
      // Show form only for roadmap agent
      setShowRoadmapForm(agentId === 'roadmap');
      // Show quiz form for quiz agent
      setShowQuizForm(agentId === 'quiz');
      setQuizStarted(false);
      setRoadmapGenerated(false);
    }
  }, [agent, navigate, agentId]); // Removed searchParams and loadChatFromId from deps

  // Handle URL chat param changes separately
  useEffect(() => {
    const chatIdFromUrl = searchParams.get('chat');
    if (chatIdFromUrl && chatIdFromUrl !== currentChatId) {
      loadChatFromId(chatIdFromUrl);
    }
  }, [searchParams, currentChatId, loadChatFromId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Chat history handlers
  const handleSelectChat = useCallback(async (chatId) => {
    setSearchParams({ chat: chatId });
    await loadChatFromId(chatId);
    setSidebarOpen(false);
  }, [setSearchParams, loadChatFromId]);

  const handleNewChat = useCallback(() => {
    setSearchParams({});
    setCurrentChatId(null);
    setMessages([{
      id: 1,
      role: 'assistant',
      content: agent.welcomeMessage,
      timestamp: new Date()
    }]);
    setShowRoadmapForm(agentId === 'roadmap');
    setShowQuizForm(agentId === 'quiz');
    setQuizStarted(false);
    setRoadmapGenerated(false);
    setSidebarOpen(false);
  }, [agent, agentId, setSearchParams]);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  const handleRoadmapFormChange = (field, value) => {
    setRoadmapForm(prev => ({ ...prev, [field]: value }));
  };

  const handleQuizFormChange = (field, value) => {
    setQuizForm(prev => ({ ...prev, [field]: value }));
  };

  const handleRoadmapFormSubmit = async (e) => {
    e.preventDefault();
    if (!roadmapForm.domain.trim()) return;

    // Create a summary message from the form
    const formSummary = `
**Domain:** ${roadmapForm.domain}
**Skills Known:** ${roadmapForm.skillsKnown || 'None specified'}
**Level:** ${roadmapForm.level.charAt(0).toUpperCase() + roadmapForm.level.slice(1)}
**Duration:** ${roadmapForm.duration}
    `.trim();

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: formSummary,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setShowRoadmapForm(false);
    setIsLoading(true);

    try {
      // Create a detailed message for the AI
      const detailedMessage = `I want to learn ${roadmapForm.domain}. I already know: ${roadmapForm.skillsKnown || 'nothing yet'}. My current level is ${roadmapForm.level}.`;
      
      const messageId = Date.now() + 1;
      const assistantMessage = {
        id: messageId,
        role: 'assistant',
        content: '',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);

      await agentService.sendMessageStream(
        {
          chat_id: currentChatId,
          agent_type: 'roadmap',
          message: detailedMessage,
          form_data: {
            domain: roadmapForm.domain,
            level: roadmapForm.level,
            duration: roadmapForm.duration,
            skillsKnown: roadmapForm.skillsKnown
          }
        },
        (chunk) => {
          setMessages(prev => prev.map(m => 
            m.id === messageId ? { ...m, content: m.content + chunk } : m
          ));
        },
        (data) => {
          setRoadmapGenerated(true);
          setIsLoading(false);
          if (data?.chat_id && !currentChatId) {
            setCurrentChatId(data.chat_id);
            setSearchParams({ chat: data.chat_id });
          }
        },
        (error) => {
          console.error('Streaming error:', error);
          setMessages(prev => prev.map(m => 
            m.id === messageId ? { 
              ...m, 
              content: m.content || 'Sorry, I encountered an error generating your roadmap. Please try again.',
              isError: !m.content 
            } : m
          ));
          setIsLoading(false);
        },
        (meta) => {
          if (meta.chat_id && !currentChatId) {
            setCurrentChatId(meta.chat_id);
            setSearchParams({ chat: meta.chat_id });
          }
        }
      );
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error generating your roadmap. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  // Quiz form submit handler
  const handleQuizFormSubmit = async (e) => {
    e.preventDefault();
    if (!quizForm.domain.trim()) return;

    // Create a summary message from the form
    const purposeText = {
      'interview': 'Interview Preparation',
      'exam': 'Exam Preparation',
      'knowledge': 'Knowledge Testing'
    }[quizForm.purpose] || quizForm.purpose;

    const formSummary = `
**Domain:** ${quizForm.domain}
**Purpose:** ${purposeText}
**Difficulty:** ${quizForm.difficulty.charAt(0).toUpperCase() + quizForm.difficulty.slice(1)}
    `.trim();

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: formSummary,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setShowQuizForm(false);
    setIsLoading(true);

    try {
      const response = await agentService.startQuizSession({
        domain: quizForm.domain,
        purpose: quizForm.purpose,
        difficulty: quizForm.difficulty
      });

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setQuizStarted(true);
      setIsLoading(false);

    } catch (error) {
      console.error('Error starting quiz:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error starting the quiz session. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  // File upload handler for Summarizer RAG
  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setIsUploading(true);

    for (const file of files) {
      try {
        const result = await agentService.uploadDocument(file, 'default');
        
        setUploadedFiles(prev => [...prev, {
          name: result.filename
        }]);

        // Add system message about uploaded file
        const uploadMessage = {
          id: Date.now(),
          role: 'system',
          content: `📄 **${result.filename}** uploaded successfully!\n\nYou can now ask questions about this document.`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, uploadMessage]);

      } catch (error) {
        console.error('Upload error:', error);
        const errorMessage = {
          id: Date.now(),
          role: 'system',
          content: `❌ Failed to upload ${file.name}: ${error.message}`,
          timestamp: new Date(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }

    setIsUploading(false);
    // Clear the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Math image upload handler
  const handleMathImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploadingMathImage(true);

    // Add user message with image preview
    const imageUrl = URL.createObjectURL(file);
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: `📷 Uploaded math problem image`,
      imageUrl: imageUrl,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);

    const messageId = Date.now() + 1;
    const assistantMessage = {
      id: messageId,
      role: 'assistant',
      content: '',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      await agentService.solveMathImageStream(
        file,
        (chunk) => {
          setMessages(prev => prev.map(m => 
            m.id === messageId ? { ...m, content: m.content + chunk } : m
          ));
        },
        () => {
          setIsLoading(false);
          setIsUploadingMathImage(false);
        },
        (error) => {
          console.error('Math image error:', error);
          setMessages(prev => prev.map(m => 
            m.id === messageId ? { 
              ...m, 
              content: m.content || `❌ Error: ${error}`,
              isError: !m.content 
            } : m
          ));
          setIsLoading(false);
          setIsUploadingMathImage(false);
        }
      );
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { 
          ...m, 
          content: m.content || 'Sorry, I encountered an error processing the image.',
          isError: !m.content 
        } : m
      ));
      setIsLoading(false);
      setIsUploadingMathImage(false);
    }

    // Clear the file input
    if (mathImageInputRef.current) {
      mathImageInputRef.current.value = '';
    }
  };

  // Clear Summarizer session
  const handleClearSession = async () => {
    try {
      await agentService.clearQASession('default');
      setUploadedFiles([]);
      setMessages([{
        id: 1,
        role: 'assistant',
        content: agent.welcomeMessage,
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Clear session error:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    const messageId = Date.now() + 1;
    const assistantMessage = {
      id: messageId,
      role: 'assistant',
      content: '',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, assistantMessage]);

    // Build form_data for agents that need it
    let formData = null;
    if (agentId === 'roadmap') {
      formData = {
        domain: roadmapForm.domain,
        level: roadmapForm.level,
        duration: roadmapForm.duration,
        skillsKnown: roadmapForm.skillsKnown
      };
    } else if (agentId === 'quiz' && quizStarted) {
      formData = {
        domain: quizForm.domain,
        purpose: quizForm.purpose,
        difficulty: quizForm.difficulty
      };
    }

    const onChunk = (chunk) => {
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { ...m, content: m.content + chunk } : m
      ));
    };

    const onComplete = (data) => {
      setIsLoading(false);
      // Update chat_id if returned (for new chats)
      if (data?.chat_id && !currentChatId) {
        setCurrentChatId(data.chat_id);
        setSearchParams({ chat: data.chat_id });
      }
    };

    const onError = (error) => {
      console.error('Streaming error:', error);
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { 
          ...m, 
          content: m.content || 'Sorry, I encountered an error. Please try again.',
          isError: !m.content 
        } : m
      ));
      setIsLoading(false);
    };

    const onMeta = (meta) => {
      // Handle chat_id from meta message
      if (meta.chat_id && !currentChatId) {
        setCurrentChatId(meta.chat_id);
        setSearchParams({ chat: meta.chat_id });
      }
    };

    try {
      // Use unified chat persistence API
      await agentService.sendMessageStream(
        {
          chat_id: currentChatId,
          agent_type: agentId,
          message: currentInput,
          form_data: formData
        },
        onChunk,
        onComplete,
        onError,
        onMeta
      );
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { 
          ...m, 
          content: m.content || 'Sorry, I encountered an error. Please try again.',
          isError: !m.content 
        } : m
      ));
      setIsLoading(false);
    }
  };

  if (!agent) {
    return null;
  }

  return (
    <div className="agent-chat-container">
      {/* Chat History Sidebar */}
      <ChatSidebar
        agentType={agentId}
        currentChatId={currentChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
      />

      {/* Main chat area wrapper */}
      <div className={`chat-main-area ${sidebarOpen ? 'sidebar-open' : ''}`}>
        {/* Header */}
        <header className="agent-chat-header" style={{ '--agent-color': agent.color }}>
          <button className="back-btn" onClick={() => navigate('/dashboard')}>
            ← Back
          </button>
          <div className="agent-info">
            <span className="agent-icon">{agent.icon}</span>
            <div>
              <h1>{agent.name}</h1>
              <p>{agent.description}</p>
          </div>
        </div>
      </header>

      {/* Roadmap Questionnaire Form */}
      {agentId === 'roadmap' && showRoadmapForm && (
        <div className="questionnaire-overlay">
          <form className="questionnaire-form" onSubmit={handleRoadmapFormSubmit}>
            <h2>📋 Tell us about your learning goals</h2>
            <p className="form-subtitle">Fill in the details below so I can create a personalized roadmap for you</p>
            
            <div className="form-group">
              <label htmlFor="domain">
                <span className="label-icon">🎯</span>
                Domain / Topic
              </label>
              <input
                type="text"
                id="domain"
                placeholder="e.g., Web Development, Machine Learning, Python, Data Science..."
                value={roadmapForm.domain}
                onChange={(e) => handleRoadmapFormChange('domain', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="skillsKnown">
                <span className="label-icon">💡</span>
                Skills Already Known
              </label>
              <textarea
                id="skillsKnown"
                placeholder="e.g., Basic HTML, CSS, some JavaScript, familiar with Git..."
                value={roadmapForm.skillsKnown}
                onChange={(e) => handleRoadmapFormChange('skillsKnown', e.target.value)}
                rows={3}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="level">
                  <span className="label-icon">📊</span>
                  Current Level
                </label>
                <select
                  id="level"
                  value={roadmapForm.level}
                  onChange={(e) => handleRoadmapFormChange('level', e.target.value)}
                >
                  <option value="beginner">🌱 Beginner</option>
                  <option value="intermediate">🌿 Intermediate</option>
                  <option value="advanced">🌳 Advanced</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="duration">
                  <span className="label-icon">⏱️</span>
                  Duration
                </label>
                <select
                  id="duration"
                  value={roadmapForm.duration}
                  onChange={(e) => handleRoadmapFormChange('duration', e.target.value)}
                >
                  <option value="1 month">1 Month</option>
                  <option value="2 months">2 Months</option>
                  <option value="3 months">3 Months</option>
                  <option value="6 months">6 Months</option>
                  <option value="1 year">1 Year</option>
                </select>
              </div>
            </div>

            <button type="submit" className="generate-btn" disabled={!roadmapForm.domain.trim()}>
              🚀 Generate My Roadmap
            </button>
          </form>
        </div>
      )}

      {/* Document Upload Panel for Summarizer Agent */}
      {agentId === 'qa' && (
        <div className="document-upload-panel">
          <div className="upload-section">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.docx,.doc,.txt,.md,.py,.js,.json,.csv"
              multiple
              style={{ display: 'none' }}
              id="file-upload"
            />
            <label htmlFor="file-upload" className={`upload-btn ${isUploading ? 'uploading' : ''}`}>
              {isUploading ? '⏳ Uploading...' : '📄 Upload Documents'}
            </label>
            <span className="upload-hint">PDF, DOCX, TXT, MD, Code files</span>
          </div>
          
          {uploadedFiles.length > 0 && (
            <div className="uploaded-files">
              <div className="files-header">
                <span>📚 Uploaded Documents ({uploadedFiles.length})</span>
                <button className="clear-btn" onClick={handleClearSession} title="Clear all documents">
                  🗑️
                </button>
              </div>
              <div className="files-list">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="file-item">
                    <span className="file-icon">📄</span>
                    <span className="file-name">{file.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Math Image Upload Panel */}
      {agentId === 'math' && (
        <div className="math-upload-panel">
          <div className="upload-section">
            <input
              type="file"
              ref={mathImageInputRef}
              onChange={handleMathImageUpload}
              accept="image/png,image/jpeg,image/jpg,image/gif,image/bmp,image/webp"
              style={{ display: 'none' }}
              id="math-image-upload"
            />
            <label htmlFor="math-image-upload" className={`upload-btn ${isUploadingMathImage ? 'uploading' : ''}`}>
              {isUploadingMathImage ? '⏳ Processing...' : '📷 Upload Problem Image'}
            </label>
            <span className="upload-hint">Take a photo or upload an image of your math problem</span>
          </div>
        </div>
      )}

      {/* Quiz Form */}
      {agentId === 'quiz' && showQuizForm && (
        <div className="questionnaire-overlay">
          <form className="questionnaire-form" onSubmit={handleQuizFormSubmit}>
            <h2>🎯 Start Your Quiz Session</h2>
            <p className="form-subtitle">Configure your learning assessment</p>

            <div className="form-group">
              <label htmlFor="quiz-domain">
                <span className="label-icon">📚</span>
                Domain / Topic
              </label>
              <input
                type="text"
                id="quiz-domain"
                placeholder="e.g., Python, Machine Learning, React, Data Structures..."
                value={quizForm.domain}
                onChange={(e) => handleQuizFormChange('domain', e.target.value)}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="quiz-purpose">
                  <span className="label-icon">🎯</span>
                  Purpose
                </label>
                <select
                  id="quiz-purpose"
                  value={quizForm.purpose}
                  onChange={(e) => handleQuizFormChange('purpose', e.target.value)}
                >
                  <option value="interview">💼 Interview Preparation</option>
                  <option value="exam">📝 Exam Preparation</option>
                  <option value="knowledge">🧠 Knowledge Testing</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="quiz-difficulty">
                  <span className="label-icon">📊</span>
                  Difficulty
                </label>
                <select
                  id="quiz-difficulty"
                  value={quizForm.difficulty}
                  onChange={(e) => handleQuizFormChange('difficulty', e.target.value)}
                >
                  <option value="easy">🟢 Easy</option>
                  <option value="moderate">🟡 Moderate</option>
                  <option value="difficult">🔴 Difficult</option>
                </select>
              </div>
            </div>

            <button type="submit" className="generate-btn" disabled={!quizForm.domain.trim()}>
              🚀 Start Quiz
            </button>
          </form>
        </div>
      )}

      {/* Messages Area */}
      <div className={`messages-area ${(showRoadmapForm && agentId === 'roadmap') || (showQuizForm && agentId === 'quiz') ? 'blurred' : ''}`}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.role} ${message.isError ? 'error' : ''}`}
          >
            {message.role === 'assistant' && (
              <span className="message-icon" style={{ backgroundColor: agent.color }}>
                {agent.icon}
              </span>
            )}
            {message.role === 'system' && (
              <span className="message-icon system-icon">
                📄
              </span>
            )}
            <div className="message-content">
              {message.imageUrl && (
                <div className="message-image">
                  <img src={message.imageUrl} alt="Uploaded math problem" />
                </div>
              )}
              <div className="message-text" dangerouslySetInnerHTML={{ 
                __html: formatMessage(message.content) 
              }} />
              <span className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <span className="message-icon" style={{ backgroundColor: agent.color }}>
              {agent.icon}
            </span>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Hide for roadmap agent */}
      {agentId !== 'roadmap' && (
        <form className="input-area" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={agent.placeholder}
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            style={{ backgroundColor: agent.color }}
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </form>
      )}
      </div>
    </div>
  );
}

// Helper function to format message with basic markdown
function formatMessage(text) {
  // Escape HTML first (but preserve our markdown)
  let formatted = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  
  // Convert markdown-like formatting
  formatted = formatted
    // Headers
    .replace(/^### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    .replace(/^# (.*$)/gm, '<h2>$1</h2>')
    // Links - [text](url) - open in new tab
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="chat-link">$1</a>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Horizontal rule
    .replace(/^---$/gm, '<hr class="chat-divider">')
    // Line breaks
    .replace(/\n/g, '<br>')
    // Bullet points
    .replace(/^- (.*$)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>')
    // Numbered lists
    .replace(/^\d+\. (.*$)/gm, '<li>$1</li>');
  
  return formatted;
}

export default AgentChat;
