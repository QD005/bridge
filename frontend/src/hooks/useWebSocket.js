import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (executionId) => {
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!executionId) return;
    const token = localStorage.getItem('access_token');
    const wsUrl = `${import.meta.env.VITE_WS_URL}/executions/${executionId}/?Bearer=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data]);
    };
    ws.onclose = () => setConnected(false);
    ws.onerror = (err) => console.error('WS error:', err);

    return () => ws.close();
  }, [executionId]);

  return { messages, connected };
};
