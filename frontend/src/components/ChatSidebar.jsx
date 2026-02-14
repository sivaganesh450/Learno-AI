import { useState, useEffect, useCallback } from 'react';
import { agentService } from '../services/agentService';
import './ChatSidebar.css';

function ChatSidebar({ 
  agentType, 
  currentChatId, 
  onSelectChat, 
  onNewChat, 
  isOpen, 
  onToggle 
}) {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const loadChats = useCallback(async () => {
    setLoading(true);
    try {
      const chatList = await agentService.listChats(agentType, 50, 0);
      setChats(chatList);
    } catch (error) {
      console.error('Failed to load chats:', error);
    }
    setLoading(false);
  }, [agentType]);

  useEffect(() => {
    if (isOpen) {
      loadChats();
    }
  }, [isOpen, agentType, loadChats]);

  // Refresh chats when currentChatId changes (new chat created)
  useEffect(() => {
    if (currentChatId && isOpen) {
      loadChats();
    }
  }, [currentChatId, isOpen, loadChats]);

  const handleDelete = async (chatId, e) => {
    e.stopPropagation();
    if (!confirm('Delete this chat?')) return;
    
    try {
      await agentService.deleteChat(chatId);
      setChats(prev => prev.filter(c => c.chat_id !== chatId));
      if (currentChatId === chatId) {
        onNewChat();
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  const handleStartEdit = (chat, e) => {
    e.stopPropagation();
    setEditingId(chat.chat_id);
    setEditTitle(chat.title);
  };

  const handleSaveEdit = async (chatId, e) => {
    e?.stopPropagation();
    if (!editTitle.trim()) return;
    
    try {
      await agentService.updateChatTitle(chatId, editTitle);
      setChats(prev => prev.map(c => 
        c.chat_id === chatId ? { ...c, title: editTitle } : c
      ));
      setEditingId(null);
    } catch (error) {
      console.error('Failed to update title:', error);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const groupChatsByDate = (chats) => {
    const groups = {
      today: [],
      yesterday: [],
      thisWeek: [],
      older: []
    };
    
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);
    
    chats.forEach(chat => {
      const chatDate = new Date(chat.updated_at);
      if (chatDate >= today) {
        groups.today.push(chat);
      } else if (chatDate >= yesterday) {
        groups.yesterday.push(chat);
      } else if (chatDate >= weekAgo) {
        groups.thisWeek.push(chat);
      } else {
        groups.older.push(chat);
      }
    });
    
    return groups;
  };

  const groups = groupChatsByDate(chats);

  const renderChatItem = (chat) => (
    <div 
      key={chat.chat_id}
      className={`chat-item ${currentChatId === chat.chat_id ? 'active' : ''}`}
      onClick={() => onSelectChat(chat.chat_id)}
    >
      {editingId === chat.chat_id ? (
        <input
          type="text"
          className="edit-title-input"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSaveEdit(chat.chat_id, e);
            if (e.key === 'Escape') setEditingId(null);
          }}
          onBlur={(e) => handleSaveEdit(chat.chat_id, e)}
          onClick={(e) => e.stopPropagation()}
          autoFocus
        />
      ) : (
        <>
          <div className="chat-item-content">
            <span className="chat-title">{chat.title}</span>
            <span className="chat-meta">
              {chat.message_count} messages · {formatDate(chat.updated_at)}
            </span>
          </div>
          <div className="chat-actions">
            <button 
              className="action-btn edit-btn"
              onClick={(e) => handleStartEdit(chat, e)}
              title="Rename"
            >
              ✏️
            </button>
            <button 
              className="action-btn delete-btn"
              onClick={(e) => handleDelete(chat.chat_id, e)}
              title="Delete"
            >
              🗑️
            </button>
          </div>
        </>
      )}
    </div>
  );

  const renderGroup = (title, chatList) => {
    if (chatList.length === 0) return null;
    return (
      <div className="chat-group">
        <div className="group-title">{title}</div>
        {chatList.map(renderChatItem)}
      </div>
    );
  };

  return (
    <>
      {/* Toggle button */}
      <button 
        className={`sidebar-toggle ${isOpen ? 'open' : ''}`}
        onClick={onToggle}
        title={isOpen ? 'Hide history' : 'Show history'}
      >
        {isOpen ? '◀' : '▶'}
      </button>

      {/* Sidebar */}
      <aside className={`chat-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h3>Chat History</h3>
          <button className="new-chat-btn" onClick={onNewChat}>
            + New Chat
          </button>
        </div>

        <div className="chat-list">
          {loading ? (
            <div className="loading-chats">Loading...</div>
          ) : chats.length === 0 ? (
            <div className="no-chats">
              <span className="no-chats-icon">💬</span>
              <p>No chat history yet</p>
              <p className="no-chats-hint">Start a conversation!</p>
            </div>
          ) : (
            <>
              {renderGroup('Today', groups.today)}
              {renderGroup('Yesterday', groups.yesterday)}
              {renderGroup('This Week', groups.thisWeek)}
              {renderGroup('Older', groups.older)}
            </>
          )}
        </div>
      </aside>
    </>
  );
}

export default ChatSidebar;
