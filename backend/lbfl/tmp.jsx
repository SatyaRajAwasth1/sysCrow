import { useState, useEffect } from "react";

const socket = new WebSocket("ws://localhost:8000/logstream")

function App(){
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    socket.onmessage = (event) => {
      const logData = JSON.parse(event.data);
      setLogs((prevLogs) => [logData, ...prevLogs].slice(0, 100));
    };
  }, []);

  return (
    <div>
      <h1>Real-Time Log Stream</h1>
      <div style={{ height: "500px", overflow: "auto", border: "1px solid #ccc" }}>
        {logs.map((log, index) => (
          <p key={index} style={{ color: log.anomaly ? "red" : "black" }}>
            {log.log} {log.anomaly && "(Anomaly Detected)"}
          </p>
        ))}
      </div>
    </div>
  );
}

export default App;
