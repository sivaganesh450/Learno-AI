import api from './api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const agentService = {
  // Generate a learning roadmap (non-streaming)
  async generateRoadmap(data) {
    const response = await api.post('/agents/roadmap', {
      message: data.message,
      topic: data.topic || data.message,
      skill_level: data.skill_level || 'beginner',
      duration: data.duration || '3 months',
      skills_known: data.skills_known || ''
    });
    return response.data;
  },

  // Generate a learning roadmap with streaming
  async generateRoadmapStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/roadmap/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: data.message,
          topic: data.topic || data.message,
          skill_level: data.skill_level || 'beginner',
          duration: data.duration || '3 months',
          skills_known: data.skills_known || ''
        })
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || `Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                onChunk(data.chunk);
              } else if (data.done) {
                onComplete();
              } else if (data.error) {
                onError(data.error);
              }
            } catch (e) {
              // Ignore parse errors for incomplete JSON
            }
          }
        }
      }
    } catch (error) {
      onError(error.message);
    }
  },

  // Get learning resources (non-streaming)
  async getResources(data) {
    const response = await api.post('/agents/resources', {
      message: data.message,
      topic: data.topic || data.message,
      skill_level: data.skill_level || 'beginner',
      resource_type: data.resource_type || 'all',
      session_id: data.session_id || 'default'
    });
    return response.data;
  },

  // Get resources with streaming
  async getResourcesStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/resources/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: data.message,
          topic: data.topic || data.message,
          skill_level: data.skill_level || 'beginner',
          resource_type: data.resource_type || 'all',
          session_id: data.session_id || 'default'
        })
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || `Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                onChunk(data.chunk);
              } else if (data.done) {
                onComplete();
              } else if (data.error) {
                onError(data.error);
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
        }
      }
    } catch (error) {
      onError(error.message);
    }
  },

  // Ask a question (non-streaming)
  async askQuestion(data) {
    const response = await api.post('/agents/qa', {
      message: data.message,
      topic: data.topic || data.message
    });
    return response.data;
  },

  // Ask question with streaming (supports RAG with session_id)
  async askQuestionStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/qa/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: data.message,
          topic: data.topic || data.message,
          session_id: data.session_id || 'default'
        })
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || `Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                onChunk(data.chunk);
              } else if (data.done) {
                onComplete();
              } else if (data.error) {
                onError(data.error);
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
        }
      }
    } catch (error) {
      onError(error.message);
    }
  },

  // List all available agents
  async listAgents() {
    const response = await api.get('/agents/list');
    return response.data;
  },

  // Clear resources agent session history
  async clearResourcesHistory(sessionId = 'default') {
    const response = await api.delete(`/agents/resources/history/${sessionId}`);
    return response.data;
  },

  // ============= Q&A RAG Document Upload Methods =============

  // Upload document for RAG Q&A
  async uploadDocument(file, sessionId = 'default') {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/agents/qa/upload?session_id=${sessionId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload document');
    }
    
    return response.json();
  },

  // Get uploaded documents for session
  async getUploadedDocuments(sessionId = 'default') {
    const response = await api.get(`/agents/qa/documents/${sessionId}`);
    return response.data;
  },

  // Clear Q&A session (documents + history)
  async clearQASession(sessionId = 'default') {
    const response = await api.delete(`/agents/qa/session/${sessionId}`);
    return response.data;
  },

  // ============= Quiz Agent Methods =============

  // Start a quiz session
  async startQuizSession(data, sessionId = 'default') {
    const response = await api.post('/agents/quiz/start', {
      domain: data.domain,
      purpose: data.purpose,
      difficulty: data.difficulty,
      session_id: sessionId
    });
    return response.data;
  },

  // Send quiz message with streaming
  async quizMessageStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/quiz/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: data.message,
          session_id: data.session_id || 'default'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          onComplete();
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const json = JSON.parse(line.slice(6));
              if (json.chunk) {
                onChunk(json.chunk);
              } else if (json.done) {
                onComplete();
                return;
              } else if (json.error) {
                onError(json.error);
                return;
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Quiz stream error:', error);
      onError(error.message || 'Failed to connect to quiz agent');
    }
  },

  // Send quiz message (non-streaming)
  async quizMessage(data, sessionId = 'default') {
    const response = await api.post('/agents/quiz/message', {
      message: data.message,
      session_id: sessionId
    });
    return response.data;
  },

  // Get quiz score
  async getQuizScore(sessionId = 'default') {
    const response = await api.get(`/agents/quiz/score/${sessionId}`);
    return response.data;
  },

  // End quiz session
  async endQuizSession(sessionId = 'default') {
    const response = await api.delete(`/agents/quiz/session/${sessionId}`);
    return response.data;
  },

  // ============= Math Problem Solver Agent =============

  // Solve math problem with streaming (Chain of Thought)
  async solveMathProblemStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/math/solve/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          problem: data.problem
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const json = JSON.parse(line.slice(6));
              if (json.chunk) {
                onChunk(json.chunk);
              } else if (json.done) {
                onComplete();
                return;
              } else if (json.error) {
                onError(json.error);
                return;
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Math solver stream error:', error);
      onError(error.message || 'Failed to connect to math problem solver');
    }
  },

  // Solve math problem (non-streaming)
  async solveMathProblem(data) {
    const response = await api.post('/agents/math/solve', {
      problem: data.problem
    });
    return response.data;
  },

  // Solve math problem from image with streaming
  async solveMathImageStream(file, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/math/solve-image/stream`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: `HTTP error! status: ${response.status}` }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const json = JSON.parse(line.slice(6));
              if (json.chunk) {
                onChunk(json.chunk);
              } else if (json.done) {
                onComplete();
                return;
              } else if (json.error) {
                onError(json.error);
                return;
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Math image solver stream error:', error);
      onError(error.message || 'Failed to process math image');
    }
  },

  // ============= Job Search Agent =============

  // Search jobs with streaming (using Tavily)
  async searchJobsStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');
    
    // Parse location from query if provided (e.g., "python developer in London")
    let query = data.query;
    let location = data.location || '';
    
    const inMatch = query.match(/(.+?)\s+in\s+(.+)/i);
    if (inMatch && !data.location) {
      query = inMatch[1].trim();
      location = inMatch[2].trim();
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/agents/jobs/search/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: query,
          location: location
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const json = JSON.parse(line.slice(6));
              if (json.chunk) {
                onChunk(json.chunk);
              } else if (json.done) {
                onComplete();
                return;
              } else if (json.error) {
                onError(json.error);
                return;
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Job search stream error:', error);
      onError(error.message || 'Failed to connect to job search service');
    }
  },

  // Search jobs (non-streaming)
  async searchJobs(data) {
    const response = await api.post('/agents/jobs/search', {
      query: data.query,
      location: data.location || ''
    });
    return response.data;
  },

  // ============= Code Assistant Agent =============

  // Solve a coding problem with streaming (Generate → Execute & Reflect loop)
  async solveCodeProblemStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_BASE_URL}/agents/code/solve/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ problem: data.problem }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const json = JSON.parse(line.slice(6));
              if (json.chunk) {
                onChunk(json.chunk);
              } else if (json.done) {
                onComplete();
                return;
              } else if (json.error) {
                onError(json.error);
                return;
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Code Assistant stream error:', error);
      onError(error.message || 'Failed to connect to Code Assistant');
    }
  },

  // Solve a coding problem (non-streaming)
  async solveCodeProblem(data) {
    const response = await api.post('/agents/code/solve', {
      problem: data.problem,
    });
    return response.data;
  },

  // ============= Deep Search & Report Generator =============

  // Generate a full research report with streaming progress
  async deepSearchStream(data, onChunk, onComplete, onError) {
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_BASE_URL}/agents/deep-search/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ topic: data.topic }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const json = JSON.parse(line.slice(6));
              if (json.chunk) {
                onChunk(json.chunk);
              } else if (json.done) {
                onComplete();
                return;
              } else if (json.error) {
                onError(json.error);
                return;
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Deep Search stream error:', error);
      onError(error.message || 'Failed to connect to Deep Search agent');
    }
  },

  // Generate a full research report (non-streaming)
  async deepSearch(data) {
    const response = await api.post('/agents/deep-search', {
      topic: data.topic,
    });
    return response.data;
  },

  // ============= Chat Persistence Methods =============

  // Create a new chat session
  async createChat(agentType, title = null, initialMessage = null) {
    const response = await api.post('/agent-chats/create', {
      agent_type: agentType,
      title: title,
      initial_message: initialMessage
    });
    return response.data;
  },

  // Get list of chats for current user
  async listChats(agentType = null, limit = 50, skip = 0) {
    const params = new URLSearchParams();
    if (agentType) params.append('agent_type', agentType);
    params.append('limit', limit);
    params.append('skip', skip);
    
    const response = await api.get(`/agent-chats/list?${params.toString()}`);
    return response.data;
  },

  // Get a specific chat with all messages
  async getChat(chatId) {
    const response = await api.get(`/agent-chats/${chatId}`);
    return response.data;
  },

  // Update chat title
  async updateChatTitle(chatId, title) {
    const response = await api.put(`/agent-chats/${chatId}/title`, { title });
    return response.data;
  },

  // Delete a chat
  async deleteChat(chatId, permanent = false) {
    const response = await api.delete(`/agent-chats/${chatId}?permanent=${permanent}`);
    return response.data;
  },

  // Clear all messages from a chat
  async clearChatMessages(chatId) {
    const response = await api.delete(`/agent-chats/${chatId}/messages`);
    return response.data;
  },

  // Send message with streaming (unified endpoint)
  async sendMessageStream(data, onChunk, onComplete, onError, onMeta) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/agent-chats/send/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          chat_id: data.chat_id || null,
          agent_type: data.agent_type,
          message: data.message,
          form_data: data.form_data || null
        })
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || `Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const json = JSON.parse(line.slice(6));
              if (json.type === 'meta' && json.chat_id) {
                // Meta info with chat_id
                if (onMeta) onMeta(json);
              } else if (json.chunk) {
                onChunk(json.chunk);
              } else if (json.done) {
                onComplete(json);
                return;
              } else if (json.error) {
                onError(json.error);
                return;
              }
            } catch (e) {
              // Ignore JSON parse errors
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat stream error:', error);
      onError(error.message || 'Failed to connect to chat service');
    }
  },

  // Send message without streaming
  async sendMessage(data) {
    const response = await api.post('/agent-chats/send', {
      chat_id: data.chat_id || null,
      agent_type: data.agent_type,
      message: data.message,
      form_data: data.form_data || null
    });
    return response.data;
  }
};

export default agentService;
