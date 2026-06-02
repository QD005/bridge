import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search, Plus, MessageSquare, Send, User, Clock, CheckCheck,
  Paperclip, X, FileText, Image, Download, AlertCircle,
  CheckCircle2, Circle, CircleDot, ArrowLeft, 
  Users, Briefcase, Pin, PinOff, MoreHorizontal
} from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Modal from '../components/Modal';
import { useAuth } from '../context/AuthContext';
import { useChatWebSocket } from '../hooks/useChatWebSocket';

const TYPE_COLORS = {
  WORKFLOW: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  EXECUTION: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  INCIDENT: 'bg-red-500/10 text-red-500 border-red-500/20',
  AGENCY: 'bg-green-500/10 text-green-500 border-green-500/20',
  APPROVAL: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  DIRECT: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
};

const PRIORITY_COLORS = {
  LOW: 'text-[var(--text-muted)]',
  NORMAL: 'text-info',
  HIGH: 'text-warning',
  URGENT: 'text-danger',
};

const TASK_STATUS_OPTIONS = {
  PENDING: { label: 'Pending', color: 'text-warning bg-warning/10 border-warning/20' },
  IN_PROGRESS: { label: 'In Progress', color: 'text-info bg-info/10 border-info/20' },
  COMPLETED: { label: 'Completed', color: 'text-success bg-success/10 border-success/20' },
  CANCELLED: { label: 'Cancelled', color: 'text-[var(--text-muted)] bg-gray-500/10 border-gray-500/20' },
};

const Collaboration = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showParticipants, setShowParticipants] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const typingTimer = useRef(null);
  
  // Modals
  const [showNewModal, setShowNewModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [eligibleUsers, setEligibleUsers] = useState([]);
  
  // New conversation form
  const [newConv, setNewConv] = useState({ 
    title: '', 
    conversation_type: 'AGENCY', 
    participant_ids: [],
    workflow: '',
    execution: '',
    agency: ''
  });

  // Task form
  const [taskForm, setTaskForm] = useState({
    content: '',
    assigned_to: '',
    priority: 'NORMAL',
    due_date: ''
  });

  // File upload
  const [uploading, setUploading] = useState(false);
  const [pendingAttachments, setPendingAttachments] = useState([]);

  // Fetch initial data
  useEffect(() => { 
    fetchConversations(); 
    fetchEligibleUsers();
  }, []);

  useEffect(() => {
    if (activeConv) {
      fetchMessages(activeConv.id);
      setConversations(prev => prev.map(c => 
        c.id === activeConv.id ? { ...c, unread_count: 0 } : c
      ));
      setMobileSidebarOpen(false);
    }
  }, [activeConv?.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const res = await api.get('/collaboration/');
      setConversations(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const fetchEligibleUsers = async () => {
    try {
      const res = await api.get('/collaboration/users/');
      setEligibleUsers(res.data);
    } catch (err) { console.error(err); }
  };

  const fetchMessages = async (id) => {
    try {
      const res = await api.get(`/collaboration/${id}/messages/`);
      setMessages(res.data);
    } catch (err) { console.error(err); }
  };

  // WebSocket handlers
  const handleNewMessage = useCallback((msg) => {
    setMessages(prev => {
      if (prev.find(m => m.id === msg.id)) return prev;
      return [...prev, msg];
    });
    setConversations(prev => prev.map(c => 
      c.id === msg.conversation ? { ...c, last_message: msg, updated_at: new Date().toISOString() } : c
    ));
  }, []);

  const handleTaskUpdated = useCallback((msg) => {
    setMessages(prev => prev.map(m => m.id === msg.id ? msg : m));
  }, []);

  const handlePinUpdated = useCallback((msg) => {
    setMessages(prev => {
      const exists = prev.find(m => m.id === msg.id);
      if (!exists) return prev;
      return prev.map(m => m.id === msg.id ? { ...m, is_pinned: msg.is_pinned } : m);
    });
  }, []);

  const { connected, onlineUsers, typingUsers, sendMessage, sendTyping, updateTask, togglePin } = useChatWebSocket(
    activeConv?.id,
    handleNewMessage,
    null,
    handleTaskUpdated,
    handlePinUpdated
  );

  // Typing indicator
  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
    sendTyping(true);
    if (typingTimer.current) clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => sendTyping(false), 2000);
  };

  // Send text message
  const handleSend = async (e) => {
    e.preventDefault();
    if ((!newMessage.trim() && pendingAttachments.length === 0) || !activeConv) return;

    const payload = {
      content: newMessage.trim(),
      message_type: 'TEXT',
      attachments: pendingAttachments,
      priority: 'NORMAL'
    };

    if (connected) {
      sendMessage(payload);
      setNewMessage('');
      setPendingAttachments([]);
    } else {
      try {
        await api.post(`/collaboration/${activeConv.id}/messages/`, payload);
        setNewMessage('');
        setPendingAttachments([]);
        fetchMessages(activeConv.id);
        fetchConversations();
      } catch (err) { alert('Failed to send message'); }
    }
  };

  // Send task
  const handleSendTask = async () => {
    if (!taskForm.content.trim() || !activeConv) return;
    
    const payload = {
      content: taskForm.content,
      message_type: 'TASK',
      assigned_to: taskForm.assigned_to ? Number(taskForm.assigned_to) : null,
      priority: taskForm.priority,
      attachments: []
    };

    if (connected) {
      sendMessage(payload);
    } else {
      try {
        await api.post(`/collaboration/${activeConv.id}/messages/`, payload);
        fetchMessages(activeConv.id);
      } catch (err) { alert('Failed to create task'); }
    }
    
    setShowTaskModal(false);
    setTaskForm({ content: '', assigned_to: '', priority: 'NORMAL', due_date: '' });
  };

  // Handle task status update
  const handleTaskStatusChange = async (msgId, newStatus) => {
    if (connected) {
      updateTask(msgId, newStatus);
    } else {
      try {
        await api.post(`/collaboration/${activeConv.id}/messages/${msgId}/task/`, {
          task_status: newStatus
        });
        fetchMessages(activeConv.id);
      } catch (err) { alert('Failed to update task'); }
    }
  };

  // Handle pin/unpin
  const handleTogglePin = async (msgId) => {
    if (connected) {
      togglePin(msgId);
    } else {
      try {
        await api.post(`/collaboration/${activeConv.id}/messages/${msgId}/pin/`);
        fetchMessages(activeConv.id);
      } catch (err) { alert('Failed to pin/unpin'); }
    }
  };

  // File upload
  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file || !activeConv) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post(`/collaboration/${activeConv.id}/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setPendingAttachments(prev => [...prev, res.data]);
    } catch (err) {
      alert('Failed to upload file');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const removeAttachment = (index) => {
    setPendingAttachments(prev => prev.filter((_, i) => i !== index));
  };

  // Create conversation
  const handleCreateConv = async () => {
    try {
      const payload = { ...newConv };
      if (!payload.workflow) delete payload.workflow;
      if (!payload.execution) delete payload.execution;
      if (!payload.agency) delete payload.agency;
      
      const res = await api.post('/collaboration/', payload);
      setShowNewModal(false);
      setNewConv({ 
        title: '', conversation_type: 'AGENCY', participant_ids: [],
        workflow: '', execution: '', agency: ''
      });
      setConversations(prev => [res.data, ...prev]);
      setActiveConv(res.data);
    } catch (err) { 
      alert(err.response?.data?.detail || 'Failed to create conversation'); 
    }
  };

  // Robust current user ID
  const currentUserId = useMemo(() => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return String(payload.user_id || payload.id || user?.id);
      }
    } catch { /* ignore */ }
    return String(user?.id || '');
  }, [user?.id]);

  const currentUserEmail = user?.email || '';

  const isUserOnline = (userId) => {
    return onlineUsers.some(u => String(u.user_id) === String(userId));
  };

  const messageIsFromMe = (msg) => {
    const senderId = String(msg.sender?.id || '');
    const senderEmail = msg.sender?.email || '';
    return senderId === currentUserId || (senderEmail && senderEmail === currentUserEmail);
  };

  // Pinned messages
  const pinnedMessages = useMemo(() => {
    return messages.filter(m => m.is_pinned);
  }, [messages]);

  // All tasks for sidebar
  const allTasks = useMemo(() => {
    return messages.filter(m => m.message_type === 'TASK');
  }, [messages]);

  const filteredConvs = conversations.filter(c => 
    (c.title || `Conversation #${c.id}`).toLowerCase().includes(search.toLowerCase()) ||
    c.conversation_type?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Loading />;

  return (
    <div className="h-[calc(100vh-5rem)] flex flex-col lg:flex-row gap-0 lg:gap-4 animate-fade-in relative">
      {/* Mobile overlay */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* Conversations Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-72 lg:w-80 flex-shrink-0 glass-panel flex flex-col overflow-hidden
        transition-transform duration-300 ease-in-out
        ${mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="p-4 border-b border-[var(--border-color)]">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-[var(--text-primary)] flex items-center gap-2">
              <MessageSquare className="w-4 h-4" /> Messages
            </h3>
            <div className="flex items-center gap-2">
              <button onClick={() => setShowNewModal(true)} 
                className="p-1.5 hover:bg-accent/10 rounded-lg text-accent transition-colors">
                <Plus className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setMobileSidebarOpen(false)}
                className="lg:hidden p-1.5 hover:bg-[var(--bg-input)] rounded-lg text-[var(--text-muted)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--text-muted)]" />
            <input 
              className="input-field pl-8 text-sm py-1.5" 
              placeholder="Search conversations..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto no-scrollbar p-2 space-y-1">
          {filteredConvs.length === 0 && (
            <div className="text-center py-8 text-[var(--text-muted)] text-sm">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-30" />
              No conversations yet
            </div>
          )}
          {filteredConvs.map(conv => (
            <button
              key={conv.id}
              onClick={() => setActiveConv(conv)}
              className={`w-full text-left p-3 rounded-lg transition-all relative ${
                activeConv?.id === conv.id 
                  ? 'bg-accent/10 border border-accent/20' 
                  : 'hover:bg-[var(--bg-input)] border border-transparent'
              }`}
            >
              {(conv.unread_count > 0 || 0) > 0 && (
                <div className="absolute top-2 right-2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">
                  {conv.unread_count}
                </div>
              )}
              
              <div className="flex items-center gap-2 mb-1 pr-6">
                <span className={`text-[10px] px-1.5 py-0.5 rounded border ${TYPE_COLORS[conv.conversation_type] || TYPE_COLORS.DIRECT}`}>
                  {conv.conversation_type}
                </span>
              </div>
              <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                {conv.title || `Conversation #${conv.id}`}
              </p>
              {conv.last_message && (
                <p className="text-xs text-[var(--text-muted)] mt-1 truncate">
                  <span className="font-medium">{conv.last_message.sender?.first_name || 'Unknown'}:</span>{' '}
                  {conv.last_message.content || (conv.last_message.attachments?.length > 0 ? '📎 Attachment' : '')}
                </p>
              )}
              <p className="text-[10px] text-[var(--text-muted)] mt-1">
                {conv.participants?.length || 0} participants · {conv.message_count || 0} messages
                {allTasks.length > 0 && activeConv?.id === conv.id && (
                  <span className="ml-2 text-warning">· {allTasks.filter(t => !['COMPLETED','CANCELLED'].includes(t.task_status)).length} tasks</span>
                )}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 glass-panel flex flex-col overflow-hidden">
        {activeConv ? (
          <>
            {/* Header */}
            <div className="p-3 lg:p-4 border-b border-[var(--border-color)] flex items-center justify-between">
              <div className="flex items-center gap-2 lg:gap-3 min-w-0">
                <button 
                  onClick={() => setMobileSidebarOpen(true)} 
                  className="lg:hidden text-[var(--text-muted)] flex-shrink-0"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-[var(--text-primary)] text-sm lg:text-base truncate">
                      {activeConv.title || `Conversation #${activeConv.id}`}
                    </h3>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${TYPE_COLORS[activeConv.conversation_type] || TYPE_COLORS.DIRECT} flex-shrink-0`}>
                      {activeConv.conversation_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <div className={`w-2 h-2 rounded-full ${connected ? 'bg-success' : 'bg-danger'}`} />
                    <span className="text-xs text-[var(--text-muted)]">
                      {connected ? 'Connected' : 'Offline'} · {activeConv.participants?.length || 0} members
                    </span>
                    {onlineUsers.length > 0 && (
                      <span className="text-xs text-success hidden sm:inline">
                        {onlineUsers.length} online
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1 lg:gap-2 flex-shrink-0">
                <button 
                  onClick={() => setShowParticipants(!showParticipants)}
                  className="btn-secondary text-xs lg:text-sm py-1.5 px-2 lg:px-3 flex items-center gap-1.5"
                >
                  <Users className="w-3.5 h-3.5" /> 
                  <span className="hidden sm:inline">{showParticipants ? 'Hide' : 'Members'}</span>
                </button>
                <button 
                  onClick={() => setShowTaskModal(true)}
                  className="btn-secondary text-xs lg:text-sm py-1.5 px-2 lg:px-3 flex items-center gap-1.5"
                >
                  <Briefcase className="w-3.5 h-3.5" /> 
                  <span className="hidden sm:inline">Task</span>
                </button>
              </div>
            </div>

            {/* Participants Panel */}
            {showParticipants && (
              <div className="border-b border-[var(--border-color)] p-3 bg-[var(--bg-input)]">
                <p className="text-xs font-medium text-[var(--text-muted)] uppercase mb-2">Participants</p>
                <div className="flex flex-wrap gap-2">
                  {activeConv.participants?.map(p => {
                    const online = isUserOnline(p.id);
                    return (
                      <div key={p.id} className="flex items-center gap-1.5 text-xs bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-full px-2 py-1">
                        <div className={`w-2 h-2 rounded-full ${online ? 'bg-success' : 'bg-[var(--text-muted)]'}`} />
                        <span className="text-[var(--text-primary)]">{p.first_name} {p.last_name}</span>
                        <span className="text-[var(--text-muted)] hidden sm:inline">{p.email}</span>
                        {online && <span className="text-success text-[10px]">online</span>}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* PINNED BANNER */}
            {pinnedMessages.length > 0 && (
              <div className="border-b-2 border-accent/20 bg-accent/5">
                {pinnedMessages.map(pinned => (
                  <div key={pinned.id} className="p-3 flex items-start gap-3 relative">
                    <div className="p-1.5 bg-accent/10 rounded-lg flex-shrink-0">
                      <Pin className="w-3.5 h-3.5 text-accent" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold text-accent uppercase">📌 Pinned</span>
                        {pinned.message_type === 'TASK' && (
                          <span className={`text-[10px] px-1.5 py-0.5 rounded border ${TASK_STATUS_OPTIONS[pinned.task_status]?.color}`}>
                            {TASK_STATUS_OPTIONS[pinned.task_status]?.label}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-[var(--text-primary)] truncate">{pinned.content}</p>
                      
                      {pinned.message_type === 'TASK' && (
                        <div className="flex items-center gap-3 mt-2 flex-wrap">
                          <span className="text-xs text-[var(--text-muted)]">
                            Assigned: <span className="text-[var(--text-primary)]">
                              {pinned.assigned_to?.first_name || 'Unassigned'} {pinned.assigned_to?.last_name || ''}
                            </span>
                          </span>
                          <div className="flex items-center gap-1">
                            <span className="text-xs text-[var(--text-muted)]">Status:</span>
                            <select
                              value={pinned.task_status}
                              onChange={(e) => handleTaskStatusChange(pinned.id, e.target.value)}
                              className="text-xs bg-[var(--bg-primary)] border border-[var(--border-color)] rounded px-2 py-0.5 text-[var(--text-primary)]"
                            >
                              {Object.entries(TASK_STATUS_OPTIONS).map(([status, { label }]) => (
                                <option key={status} value={status}>{label}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}
                    </div>
                    <button 
                      onClick={() => handleTogglePin(pinned.id)}
                      className="p-1 hover:bg-danger/10 rounded text-[var(--text-muted)] hover:text-danger transition-colors flex-shrink-0"
                      title="Unpin"
                    >
                      <PinOff className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto no-scrollbar p-3 lg:p-4 space-y-3 lg:space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12 text-[var(--text-muted)]">
                  <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-20" />
                  <p>No messages yet. Start the conversation!</p>
                </div>
              )}
              {messages.map(msg => {
                const isMe = messageIsFromMe(msg);
                const isTask = msg.message_type === 'TASK';
                
                return (
                  <div key={msg.id} className={`flex gap-2 lg:gap-3 ${isMe ? 'flex-row-reverse' : 'flex-row'}`}>
                    {/* Avatar */}
                    <div className="flex flex-col items-center gap-1 flex-shrink-0">
                      <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-accent/10 flex items-center justify-center relative">
                        <User className="w-3.5 h-3.5 lg:w-4 lg:h-4 text-accent" />
                        {isUserOnline(msg.sender?.id) && (
                          <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 lg:w-2.5 lg:h-2.5 rounded-full bg-success border-2 border-[var(--bg-panel)]" />
                        )}
                      </div>
                    </div>

                    {/* Message bubble */}
                    <div className={`flex flex-col max-w-[80%] lg:max-w-[75%] ${isMe ? 'items-end' : 'items-start'}`}>
                      {/* Name & time */}
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-[var(--text-secondary)]">
                          {isMe ? 'You' : `${msg.sender?.first_name || 'Unknown'} ${msg.sender?.last_name || ''}`}
                        </span>
                        <span className="text-[10px] text-[var(--text-muted)] flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {msg.priority !== 'NORMAL' && (
                          <AlertCircle className={`w-3 h-3 ${PRIORITY_COLORS[msg.priority]}`} />
                        )}
                      </div>

                      <div className={`p-2.5 lg:p-3 rounded-2xl group relative ${
                        isMe 
                          ? 'bg-accent text-white rounded-tr-sm' 
                          : 'bg-[var(--bg-input)] text-[var(--text-primary)] border border-[var(--border-color)] rounded-tl-sm'
                      }`}>
                        {/* Hover action menu */}
                        <div className={`absolute top-1 ${isMe ? 'left-1' : 'right-1'} opacity-0 group-hover:opacity-100 transition-opacity`}>
                          <button 
                            onClick={() => handleTogglePin(msg.id)}
                            className={`p-1 rounded ${isMe ? 'hover:bg-white/20' : 'hover:bg-[var(--bg-primary)]'} text-[10px]`}
                            title={msg.is_pinned ? "Unpin" : "Pin"}
                          >
                            {msg.is_pinned ? <PinOff className="w-3 h-3" /> : <Pin className="w-3 h-3" />}
                          </button>
                        </div>

                        {/* Task Badge */}
                        {isTask && (
                          <div className={`flex items-center gap-2 mb-2 pb-2 border-b ${isMe ? 'border-white/20' : 'border-[var(--border-color)]'}`}>
                            <Briefcase className="w-3.5 h-3.5" />
                            <span className="text-xs font-semibold">TASK</span>
                            <span className={`text-[10px] px-1.5 py-0.5 rounded border ${TASK_STATUS_OPTIONS[msg.task_status]?.color}`}>
                              {TASK_STATUS_OPTIONS[msg.task_status]?.label}
                            </span>
                            {msg.is_pinned && <Pin className="w-3 h-3 ml-1" />}
                          </div>
                        )}

                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>

                        {/* Attachments */}
                        {msg.attachments?.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {msg.attachments.map((att, i) => (
                              <a 
                                key={i}
                                href={att.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`flex items-center gap-2 p-2 rounded-lg text-xs ${
                                  isMe ? 'bg-white/10' : 'bg-[var(--bg-primary)]'
                                } hover:opacity-80 transition-opacity`}
                              >
                                {att.type?.startsWith('image/') ? <Image className="w-3.5 h-3.5" /> : <FileText className="w-3.5 h-3.5" />}
                                <span className="truncate flex-1">{att.name}</span>
                                <Download className="w-3.5 h-3.5" />
                              </a>
                            ))}
                          </div>
                        )}

                        {/* Task status buttons inside message */}
                        {isTask && (
                          <div className={`mt-2 pt-2 ${isMe ? 'border-t border-white/20' : 'border-t border-[var(--border-color)]'}`}>
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-[10px] opacity-80">
                                {msg.assigned_to ? `To: ${msg.assigned_to.first_name}` : 'Unassigned'}
                              </span>
                              <div className="flex items-center gap-1 flex-wrap">
                                {Object.entries(TASK_STATUS_OPTIONS).map(([status, { label, color }]) => (
                                  <button
                                    key={status}
                                    onClick={() => handleTaskStatusChange(msg.id, status)}
                                    className={`text-[10px] px-2 py-0.5 rounded border transition-all ${
                                      msg.task_status === status 
                                        ? color + ' font-semibold' 
                                        : 'border-[var(--border-color)] text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                                    }`}
                                  >
                                    {label}
                                  </button>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Read receipt */}
                      <div className="flex items-center gap-1 mt-1">
                        {isMe && (
                          <>
                            <CheckCheck className={`w-3 h-3 ${msg.read_by?.length > 1 ? 'text-success' : 'text-[var(--text-muted)]'}`} />
                            <span className="text-[10px] text-[var(--text-muted)]">
                              {msg.read_by?.length > 1 ? 'Read' : 'Sent'}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {/* Typing indicator */}
              {typingUsers.length > 0 && (
                <div className="flex items-center gap-2 text-xs text-[var(--text-muted)] pl-9 lg:pl-11">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-[var(--text-muted)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 bg-[var(--text-muted)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 bg-[var(--text-muted)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  {typingUsers.map(u => u.user_name).join(', ')} typing...
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-3 lg:p-4 border-t border-[var(--border-color)]">
              {pendingAttachments.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {pendingAttachments.map((att, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg px-2 py-1">
                      <FileText className="w-3 h-3" />
                      <span className="truncate max-w-[100px] lg:max-w-[150px]">{att.name}</span>
                      <button onClick={() => removeAttachment(i)} className="text-danger hover:opacity-70">
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              <form onSubmit={handleSend} className="flex gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  onChange={handleFileSelect}
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  className="p-2 lg:p-2.5 hover:bg-[var(--bg-input)] rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors flex-shrink-0"
                >
                  <Paperclip className="w-4 h-4 lg:w-5 lg:h-5" />
                </button>
                <input
                  className="input-field flex-1 text-sm"
                  value={newMessage}
                  onChange={handleInputChange}
                  placeholder={uploading ? 'Uploading...' : 'Type a message...'}
                  disabled={uploading}
                />
                <button 
                  type="submit" 
                  disabled={uploading || (!newMessage.trim() && pendingAttachments.length === 0)}
                  className="btn-primary px-3 lg:px-4 disabled:opacity-50 flex-shrink-0"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-[var(--text-muted)]">
            <div className="text-center px-4">
              <MessageSquare className="w-12 h-12 lg:w-16 lg:h-16 mx-auto mb-4 opacity-20" />
              <p className="text-base lg:text-lg font-medium mb-1">Select a conversation</p>
              <p className="text-sm">Choose a conversation to start messaging with agency partners</p>
              <button 
                onClick={() => setMobileSidebarOpen(true)}
                className="mt-4 btn-primary lg:hidden"
              >
                View Conversations
              </button>
            </div>
          </div>
        )}
      </div>

      {/* New Conversation Modal */}
      <Modal isOpen={showNewModal} onClose={() => setShowNewModal(false)} title="New Conversation" size="md">
        <div className="space-y-4">
          <div>
            <label className="label">Title</label>
            <input className="input-field" value={newConv.title} 
              onChange={e => setNewConv({...newConv, title: e.target.value})} 
              placeholder="e.g. KCCA License Discussion" required />
          </div>
          <div>
            <label className="label">Type</label>
            <select className="input-field" value={newConv.conversation_type} 
              onChange={e => setNewConv({...newConv, conversation_type: e.target.value})}>
              {['DIRECT','WORKFLOW','EXECUTION','INCIDENT','AGENCY','APPROVAL'].map(t => (
                <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label flex items-center gap-2">
              <Users className="w-3.5 h-3.5" /> Participants ({newConv.participant_ids.length})
            </label>
            <div className="max-h-40 overflow-y-auto no-scrollbar border border-[var(--border-color)] rounded-lg p-2 space-y-1">
              {eligibleUsers.map(u => (
                <label key={u.id} className="flex items-center gap-2 p-2 hover:bg-[var(--bg-input)] rounded cursor-pointer">
                  <input
                    type="checkbox"
                    className="rounded border-[var(--border-color)] text-accent"
                    checked={newConv.participant_ids.includes(u.id)}
                    onChange={e => {
                      if (e.target.checked) {
                        setNewConv(prev => ({...prev, participant_ids: [...prev.participant_ids, u.id]}));
                      } else {
                        setNewConv(prev => ({...prev, participant_ids: prev.participant_ids.filter(id => id !== u.id)}));
                      }
                    }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-[var(--text-primary)]">{u.first_name} {u.last_name}</p>
                    <p className="text-[10px] text-[var(--text-muted)]">{u.email} · {u.agency_name || u.agency?.name || 'No agency'}</p>
                  </div>
                </label>
              ))}
              {eligibleUsers.length === 0 && (
                <p className="text-xs text-[var(--text-muted)] text-center py-2">No eligible users found</p>
              )}
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setShowNewModal(false)} className="btn-secondary">Cancel</button>
            <button onClick={handleCreateConv} className="btn-primary">Create Conversation</button>
          </div>
        </div>
      </Modal>

      {/* Assign Task Modal */}
      <Modal isOpen={showTaskModal} onClose={() => setShowTaskModal(false)} title="Assign Task" size="sm">
        <div className="space-y-4">
          <div>
            <label className="label">Task Description</label>
            <textarea className="input-field" rows={3} value={taskForm.content}
              onChange={e => setTaskForm({...taskForm, content: e.target.value})}
              placeholder="Describe the task..." required />
          </div>
          <div>
            <label className="label flex items-center gap-2"><Users className="w-3.5 h-3.5" /> Assign To</label>
            <select className="input-field" value={taskForm.assigned_to}
              onChange={e => setTaskForm({...taskForm, assigned_to: e.target.value})}>
              <option value="">Select user...</option>
              {activeConv?.participants?.map(p => (
                <option key={p.id} value={p.id}>{p.first_name} {p.last_name} ({p.email})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Priority</label>
            <select className="input-field" value={taskForm.priority}
              onChange={e => setTaskForm({...taskForm, priority: e.target.value})}>
              {['LOW','NORMAL','HIGH','URGENT'].map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setShowTaskModal(false)} className="btn-secondary">Cancel</button>
            <button onClick={handleSendTask} className="btn-primary flex items-center gap-2">
              <Briefcase className="w-4 h-4" /> Assign Task
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Collaboration;