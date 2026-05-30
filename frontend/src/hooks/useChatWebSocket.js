import { useEffect, useRef, useState, useCallback } from 'react';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000';

export const useChatWebSocket = (conversationId, onMessage, onTyping, onTaskUpdated, onPin) => {
  const [connected, setConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [typingUsers, setTypingUsers] = useState([]);
  const ws = useRef(null);
  const typingTimeout = useRef({});

  useEffect(() => {
    if (!conversationId) {
      setOnlineUsers([]);
      setConnected(false);
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) return;

    const wsUrl = `${WS_BASE_URL}/ws/chat/${conversationId}/?token=${token}`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setConnected(true);
      socket.send(JSON.stringify({ action: 'get_presence' }));
    };

    socket.onclose = () => {
      setConnected(false);
      setOnlineUsers([]);
      setTypingUsers([]);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'message':
          onMessage?.(data.data);
          break;
        case 'typing':
          if (data.data.is_typing) {
            setTypingUsers(prev => {
              const filtered = prev.filter(u => u.user_id !== data.data.user_id);
              return [...filtered, { user_id: data.data.user_id, user_name: data.data.user_name }];
            });
            if (typingTimeout.current[data.data.user_id]) {
              clearTimeout(typingTimeout.current[data.data.user_id]);
            }
            typingTimeout.current[data.data.user_id] = setTimeout(() => {
              setTypingUsers(prev => prev.filter(u => u.user_id !== data.data.user_id));
            }, 3000);
          } else {
            setTypingUsers(prev => prev.filter(u => u.user_id !== data.data.user_id));
          }
          break;
        case 'read':
          break;
        case 'task_updated':
          onTaskUpdated?.(data.data);
          break;
        case 'pin':
          onPin?.(data.data);
          break;
        case 'presence':
          setOnlineUsers(data.users || []);
          break;
        case 'error':
          console.error('WebSocket error:', data.detail);
          break;
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.current = socket;

    return () => {
      socket.close();
      Object.values(typingTimeout.current).forEach(clearTimeout);
    };
  }, [conversationId, onMessage, onTyping, onTaskUpdated, onPin]);

  const sendMessage = useCallback((payload) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'message', ...payload }));
    }
  }, []);

  const sendTyping = useCallback((isTyping) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'typing', is_typing: isTyping }));
    }
  }, []);

  const markRead = useCallback((messageId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'read', message_id: messageId }));
    }
  }, []);

  const updateTask = useCallback((messageId, taskStatus) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ 
        action: 'task_update', 
        message_id: messageId, 
        task_status: taskStatus 
      }));
    }
  }, []);

  const togglePin = useCallback((messageId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ 
        action: 'pin', 
        message_id: messageId 
      }));
    }
  }, []);

  return { connected, onlineUsers, typingUsers, sendMessage, sendTyping, markRead, updateTask, togglePin };
};