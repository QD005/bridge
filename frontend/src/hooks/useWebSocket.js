import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (executionId) => {
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT = 10;
  const BASE_DELAY = 2000;

  useEffect(() => {
    if (!executionId) return;

    let mounted = true;
    let ws = null;

    const connect = () => {
      const token = localStorage.getItem('access_token');
      if (!token || !mounted) return;

      // Build URL
      const base = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws';
      const cleanBase = base.replace(/\/$/, '');
      // Most Django JWT middlewares expect ?token=, not ?Bearer=
      const wsUrl = `${cleanBase}/executions/${executionId}/?token=${token}`;

      if (reconnectAttempts.current < 3) {
        console.log('Execution WS connecting...');
      }

      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mounted) {
          ws.close();
          return;
        }
        reconnectAttempts.current = 0;
        setConnected(true);
      };

      ws.onmessage = (event) => {
        if (!mounted) return;
        try {
          const data = JSON.parse(event.data);
          setMessages(prev => [...prev, data]);
        } catch {
          setMessages(prev => [...prev, event.data]);
        }
      };

      ws.onclose = (e) => {
        if (!mounted) return;
        setConnected(false);
        if (e.code !== 1000 && reconnectAttempts.current < MAX_RECONNECT) {
          reconnectAttempts.current += 1;
          const delay = Math.min(BASE_DELAY * reconnectAttempts.current, 30000);
          reconnectTimer.current = setTimeout(connect, delay);
        } else if (reconnectAttempts.current >= MAX_RECONNECT) {
          console.warn('Execution WS: max reconnect attempts reached.');
        }
      };

      ws.onerror = () => {
        // Empty — browser hides WS failure details. onclose handles backoff.
      };
    };

    // StrictMode-safe: delay by one tick so React's synthetic unmount
    // can cancel the timer before any socket is created.
    const startTimer = setTimeout(() => {
      if (mounted) connect();
    }, 0);

    return () => {
      mounted = false;
      clearTimeout(startTimer);
      clearTimeout(reconnectTimer.current);
      if (ws) {
        ws.onopen = null;
        ws.onmessage = null;
        ws.onclose = null;
        ws.onerror = null;
        ws.close();
      }
      wsRef.current = null;
    };
  }, [executionId]);

  return { messages, connected };
};