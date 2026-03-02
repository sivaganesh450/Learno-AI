import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const agents = [
    {
      id: 'roadmap',
      name: 'Roadmap Generator',
      description: 'Create personalized learning paths tailored to your goals and skill level. Get a structured plan to achieve your learning objectives.',
      icon: '🗺️',
      color: '#1e88e5',
      bgColor: '#e3f2fd'
    },
    {
      id: 'resources',
      name: 'Resources Provider',
      description: 'Access curated learning materials, tutorials, and resources. Find the best content from across the web, organized just for you.',
      icon: '📚',
      color: '#0d47a1',
      bgColor: '#bbdefb'
    },
    {
      id: 'qa',
      name: 'Summarizer',
      description: 'Upload documents and get AI-powered summaries, insights, and answers to your questions.',
      icon: '📄',
      color: '#64b5f6',
      bgColor: '#e1f5fe'
    },
    {
      id: 'quiz',
      name: 'Question Answering System',
      description: 'Interactive Q&A for interview prep, exam preparation, and knowledge testing. Get rated and receive feedback on your answers.',
      icon: '❓',
      color: '#ff9800',
      bgColor: '#fff3e0'
    },
    {
      id: 'math',
      name: 'Problem Solver',
      description: 'Solve complex math problems step-by-step using Chain of Thought reasoning. Supports algebra, calculus, geometry, and more.',
      icon: '🧮',
      color: '#9c27b0',
      bgColor: '#f3e5f5'
    },
    {
      id: 'jobs',
      name: 'Job Search',
      description: 'Search for recent job listings worldwide using Adzuna. Find opportunities in tech, finance, healthcare, and more.',
      icon: '💼',
      color: '#4caf50',
      bgColor: '#e8f5e9'
    },
    {
      id: 'code_assistant',
      name: 'Code Assistant',
      description: 'Solve coding problems with AI-powered code generation and automatic error correction. Iteratively refines code until it runs correctly.',
      icon: '👨‍💻',
      color: '#00897b',
      bgColor: '#e0f2f1'
    },
    {
      id: 'deep_search',
      name: 'Deep Search & Report Generator',
      description: 'Generate comprehensive research reports on any topic. Uses parallel AI agents to research, write and refine every section with live web data.',
      icon: '📊',
      color: '#6d4c41',
      bgColor: '#efebe9'
    }
  ];

  const features = [
    {
      icon: '🎯',
      title: 'Goal-Oriented Learning',
      description: 'Set your goals and let our platform guide you with a clear path to success.',
      color: '#1e88e5',
      bgColor: '#e3f2fd'
    },
    {
      icon: '✨',
      title: 'AI-Powered Assistance',
      description: 'Leverage cutting-edge AI technology to enhance your learning experience.',
      color: '#0d47a1',
      bgColor: '#bbdefb'
    },
    {
      icon: '👥',
      title: 'Community Support',
      description: 'Join a community of learners and grow together with shared knowledge.',
      color: '#64b5f6',
      bgColor: '#e1f5fe'
    },
    {
      icon: '📈',
      title: 'Track Progress',
      description: 'Monitor your learning journey with detailed analytics and milestones.',
      color: '#1565c0',
      bgColor: '#e3f2fd'
    }
  ];

  const handleConnectAgent = (agentId) => {
    navigate(`/agent/${agentId}`);
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1 className="logo">Learn<span className="logo-accent">O</span></h1>
        </div>
        <div className="header-right">
          <span className="user-name">Welcome, {user?.full_name}</span>
          <button className="logout-btn" onClick={logout}>Logout</button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <h1 className="hero-title">Welcome to <span className="gradient-text">LearnO</span></h1>
        <p className="hero-subtitle">
          Your intelligent learning companion powered by AI agents. Start your personalized learning journey today.
        </p>
      </section>

      {/* Agents Section */}
      <section className="agents-section">
        <div className="agents-grid">
          {agents.map((agent) => (
            <div 
              key={agent.id} 
              className="agent-card"
              style={{ borderColor: agent.color }}
            >
              <div 
                className="agent-icon"
                style={{ backgroundColor: agent.bgColor }}
              >
                <span style={{ fontSize: '2rem' }}>{agent.icon}</span>
              </div>
              <h3 className="agent-name">{agent.name}</h3>
              <p className="agent-description">{agent.description}</p>
              <button 
                className="connect-btn"
                style={{ backgroundColor: agent.color }}
                onClick={() => handleConnectAgent(agent.id)}
              >
                Connect Agent
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Why Choose Section */}
      <section className="why-choose-section">
        <h2 className="section-title">Why Choose LearnO?</h2>
        <p className="section-subtitle">
          LearnO combines the power of AI with a user-friendly interface to make learning more accessible, efficient, and enjoyable for everyone.
        </p>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div 
                className="feature-icon"
                style={{ backgroundColor: feature.bgColor }}
              >
                <span style={{ fontSize: '1.5rem' }}>{feature.icon}</span>
              </div>
              <h4 className="feature-title">{feature.title}</h4>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="how-it-works-content">
          <div className="how-it-works-left">
            <h2 className="section-title-left">How It Works</h2>
            <div className="steps">
              <div className="step">
                <span className="step-number" style={{ backgroundColor: '#7c3aed' }}>1</span>
                <div className="step-content">
                  <h4>Choose Your Agent</h4>
                  <p>Select from our six powerful AI agents based on your needs.</p>
                </div>
              </div>
              <div className="step">
                <span className="step-number" style={{ backgroundColor: '#06b6d4' }}>2</span>
                <div className="step-content">
                  <h4>Get Personalized Assistance</h4>
                  <p>Receive tailored recommendations and guidance for your learning journey.</p>
                </div>
              </div>
              <div className="step">
                <span className="step-number" style={{ backgroundColor: '#ec4899' }}>3</span>
                <div className="step-content">
                  <h4>Achieve Your Goals</h4>
                  <p>Follow your customized roadmap and reach your learning objectives faster.</p>
                </div>
              </div>
            </div>
          </div>
          <div className="how-it-works-right">
            <h2 className="section-title-left">Our Mission</h2>
            <p className="mission-text">
              At LearnO, we believe that learning should be accessible, personalized, and engaging for everyone. Our platform leverages advanced AI technology to break down complex topics, provide structured learning paths, and offer instant support whenever you need it.
            </p>
            <p className="mission-text">
              Whether you're a student, professional, or lifelong learner, LearnO adapts to your unique learning style and helps you achieve your educational goals with confidence.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-number" style={{ color: '#7c3aed' }}>6</span>
            <span className="stat-label">AI Agents</span>
          </div>
          <div className="stat-item">
            <span className="stat-number" style={{ color: '#ec4899' }}>24/7</span>
            <span className="stat-label">Availability</span>
          </div>
          <div className="stat-item">
            <span className="stat-number" style={{ color: '#ec4899' }}>∞</span>
            <span className="stat-label">Learning Possibilities</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>© 2026 LearnO. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Dashboard;
