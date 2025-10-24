import { useState, useEffect, useRef } from "react";

export default function LogStream() {
  const [logs, setLogs] = useState([]);
  const logContainerRef = useRef(null);
  
  useEffect(() => {
    // WebSocket connection
    let ws = null;
    
    ws = new WebSocket("ws://localhost:9000/modelstream");
      
      ws.onopen = () => {
        console.log('WebSocket connected');
      };
      
      ws.onmessage = (event) => {
      setLogs((prevLogs) => [event.data, ...prevLogs].slice(0, 1000));
    };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
      };

      return () => ws.close();
    
  }, []);
  
  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);
  
  
  return (
    <div ref={logContainerRef} className="h-70 w-full overflow-auto bg-gray-800 p-3 rounded-lg font-mono text-sm">
      {logs.map(log => (
        <div className="mb-1">
          <span className="text-gray-300">{log}</span>
        </div>
      ))}
    </div>
  );
}