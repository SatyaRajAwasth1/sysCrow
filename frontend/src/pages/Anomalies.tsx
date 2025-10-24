import { useState, useEffect } from "react";
import { AlertTriangle, Clock, X, AlertCircle, ChevronRight } from "lucide-react";

const dummyAnomalies = [
  {
    id: 1,
    timestamp: "2025-02-20T08:43:12Z",
    modelName: "Log Pattern Analyzer",
    severity: "Critical",
    description: "Unexpected authentication failure pattern detected",
    anomalousLogs: [
      "2025-02-20T08:42:58Z [ERROR] Authentication failed for user admin from IP 203.0.113.42",
      "2025-02-20T08:43:01Z [ERROR] Authentication failed for user admin from IP 203.0.113.42",
      "2025-02-20T08:43:05Z [ERROR] Authentication failed for user admin from IP 203.0.113.42"
    ],
    diagnosticInfo: "Multiple failed authentication attempts from same IP within short timeframe. Potential brute force attack signature identified."
  },
  {
    id: 2,
    timestamp: "2025-02-20T10:15:37Z",
    modelName: "Resource Monitor ML",
    severity: "Warning",
    description: "CPU utilization anomaly detected on production server",
    anomalousLogs: [
      "2025-02-20T10:14:22Z [WARN] System load average exceeds threshold: 8.76",
      "2025-02-20T10:14:52Z [WARN] Process 'database-service' consuming 87% CPU",
      "2025-02-20T10:15:22Z [WARN] System load continuing to increase: 9.33"
    ],
    diagnosticInfo: "Unexpected CPU utilization pattern detected outside normal operational hours. No corresponding scheduled jobs or backup operations found."
  },
  {
    id: 3,
    timestamp: "2025-02-20T12:01:45Z",
    modelName: "Network Traffic Analyzer",
    severity: "Medium",
    description: "Unusual outbound data transfer detected",
    anomalousLogs: [
      "2025-02-20T12:00:12Z [INFO] Outbound transfer to 192.0.2.155 - 250MB",
      "2025-02-20T12:00:45Z [INFO] Outbound transfer to 192.0.2.155 - 340MB",
      "2025-02-20T12:01:18Z [INFO] Outbound transfer to 192.0.2.155 - 410MB"
    ],
    diagnosticInfo: "Large outbound data transfer to unrecognized IP address. Transfer pattern does not match known application behavior profiles."
  },
  {
    id: 4,
    timestamp: "2025-02-20T13:27:19Z",
    modelName: "Log Semantic Analyzer",
    severity: "Low",
    description: "Configuration change detected outside maintenance window",
    anomalousLogs: [
      "2025-02-20T13:26:45Z [INFO] User 'sysadmin' modified firewall configuration",
      "2025-02-20T13:27:02Z [INFO] Firewall rule #23 updated: port range expanded",
      "2025-02-20T13:27:19Z [INFO] Firewall configuration changes applied"
    ],
    diagnosticInfo: "Configuration change performed outside scheduled maintenance window (Tuesdays 02:00-04:00). Change not associated with any approved change request in tracking system."
  },
  {
    id: 5,
    timestamp: "2025-02-20T13:27:19Z",
    modelName: "Log Semantic Analyzer",
    severity: "Low",
    description: "Configuration change detected outside maintenance window",
    anomalousLogs: [
      "2025-02-20T13:26:45Z [INFO] User 'sysadmin' modified firewall configuration",
      "2025-02-20T13:27:02Z [INFO] Firewall rule #23 updated: port range expanded",
      "2025-02-20T13:27:19Z [INFO] Firewall configuration changes applied"
    ],
    diagnosticInfo: "Configuration change performed outside scheduled maintenance window (Tuesdays 02:00-04:00). Change not associated with any approved change request in tracking system."
  },
  {
    id: 6,
    timestamp: "2025-02-20T13:27:19Z",
    modelName: "Log Semantic Analyzer",
    severity: "Low",
    description: "Configuration change detected outside maintenance window",
    anomalousLogs: [
      "2025-02-20T13:26:45Z [INFO] User 'sysadmin' modified firewall configuration",
      "2025-02-20T13:27:02Z [INFO] Firewall rule #23 updated: port range expanded",
      "2025-02-20T13:27:19Z [INFO] Firewall configuration changes applied"
    ],
    diagnosticInfo: "Configuration change performed outside scheduled maintenance window (Tuesdays 02:00-04:00). Change not associated with any approved change request in tracking system."
  },
  {
    id: 7,
    timestamp: "2025-02-20T13:27:19Z",
    modelName: "Log Semantic Analyzer",
    severity: "Low",
    description: "Configuration change detected outside maintenance window",
    anomalousLogs: [
      "2025-02-20T13:26:45Z [INFO] User 'sysadmin' modified firewall configuration",
      "2025-02-20T13:27:02Z [INFO] Firewall rule #23 updated: port range expanded",
      "2025-02-20T13:27:19Z [INFO] Firewall configuration changes applied"
    ],
    diagnosticInfo: "Configuration change performed outside scheduled maintenance window (Tuesdays 02:00-04:00). Change not associated with any approved change request in tracking system."
  }
];

// Severity badge component
function SeverityBadge({ severity }) {
  const severityConfig = {
    "Critical": { bgColor: "bg-red-500/20", textColor: "text-red-500", icon: AlertCircle },
    "High": { bgColor: "bg-orange-500/20", textColor: "text-orange-500", icon: AlertTriangle },
    "Medium": { bgColor: "bg-yellow-500/20", textColor: "text-yellow-500", icon: AlertTriangle },
    "Warning": { bgColor: "bg-yellow-500/20", textColor: "text-yellow-500", icon: AlertTriangle },
    "Low": { bgColor: "bg-blue-500/20", textColor: "text-blue-500", icon: AlertTriangle }
  };
  
  const config = severityConfig[severity] || severityConfig["Medium"];
  const Icon = config.icon;
  
  return (
    <div className={`flex items-center gap-1 rounded-full px-2 py-1 ${config.bgColor} ${config.textColor} text-xs font-medium`}>
      <Icon size={12} />
      <span>{severity}</span>
    </div>
  );
}

function formatDateTime(isoString) {
  const date = new Date(isoString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).format(date);
}

// API service
/* 
const anomalyService = {
  getAnomalies: async () => {
    try {
      const response = await fetch('/api/anomalies');
      if (!response.ok) {
        throw new Error('Failed to fetch anomalies');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      return [];
    }
  },
  
  getAnomalyDetails: async (id) => {
    try {
      const response = await fetch(`/api/anomalies/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch anomaly details');
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching anomaly details for ID ${id}:`, error);
      return null;
    }
  }
};
*/

const mockAnomalyService = {
  getAnomalies: () => {
    // Simulate network delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(dummyAnomalies);
      }, 500); // 500ms delay to simulate API call
    });
  },
  
  getAnomalyDetails: (id) => {
    // Simulate network delay
    return new Promise((resolve) => {
      setTimeout(() => {
        const anomaly = dummyAnomalies.find(a => a.id === id);
        resolve(anomaly);
      }, 300); // 300ms delay to simulate API call
    });
  }
};

// Main component
function AnomalyDetectionDashboard() {
  const [anomalies, setAnomalies] = useState([]);
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch anomalies on component mount (using mock service for demo)
  useEffect(() => {
    const fetchAnomalies = async () => {
      setLoading(true);
      try {
        // For production, replace mockAnomalyService with real API service
        const data = await mockAnomalyService.getAnomalies();
        setAnomalies(data);
        setError(null);
      } catch (err) {
        setError('Failed to load anomalies. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnomalies();
    
    // Uncomment for production to enable polling
    /*
    const intervalId = setInterval(fetchAnomalies, 60000); // Refresh every minute
    return () => clearInterval(intervalId);
    */
  }, []);
  
  const handleAnomalyClick = async (anomaly) => {
    try {
      // For production, replace mockAnomalyService with real API service
      const detailedAnomaly = await mockAnomalyService.getAnomalyDetails(anomaly.id);
      setSelectedAnomaly(detailedAnomaly || anomaly);
      setShowModal(true);
    } catch (err) {
      console.error('Error fetching anomaly details:', err);
      // Fall back to using the list item data
      setSelectedAnomaly(anomaly);
      setShowModal(true);
    }
  };
  
  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Fixed Header */}
      {/* <div className="fixed top-0 left-0 right-0 bg-black z-10 pt-4 pb-2 px-6 ml-16 border-b border-gray-800">
        <h2 className="text-xl font-bold flex items-center">
          <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
          Detected Anomalies
        </h2>
      </div> */}
      
      <div className="flex pt-0 mt-0"> {/* Adjusted padding to account for fixed header */}
        {/* Main content */}
        <main className="flex-1 p-6 pt-0 overflow-y-auto min-h-screen ml-8 mr-8 mt-0">
          <div className="grid grid-cols-12 gap-4">
            <div className="col-span-12 flex items-center mb-2">
              <div className="flex items-center gap-3">
                {/* Optional controls can go here */}
              </div>
            </div>
            
            {/* Anomalies List */}
            <div className="col-span-12">
              <div className="bg-gray-800/70 rounded-lg overflow-hidden">
                <div className="flex justify-between items-center px-4 py-2 border-b border-gray-700/50">
                  <h3 className="font-medium text-gray-300">Detected Anomalies</h3>
                  <div className="flex items-center gap-2">
                    {loading && <span className="text-xs text-gray-400">Refreshing...</span>}
                  </div>
                </div>
                
                {error && (
                  <div className="p-4 text-red-400 flex items-center gap-2">
                    <AlertCircle size={16} />
                    <span>{error}</span>
                  </div>
                )}
                
                {loading && anomalies.length === 0 ? (
                  <div className="p-6 text-center text-gray-400">Loading anomalies...</div>
                ) : anomalies.length === 0 ? (
                  <div className="p-6 text-center text-gray-400">No anomalies detected</div>
                ) : (
                  <div className="divide-y divide-gray-700/30">
                    {anomalies.map((anomaly) => (
                      <div 
                        key={anomaly.id}
                        onClick={() => handleAnomalyClick(anomaly)}
                        className="p-4 hover:bg-gray-700/30 cursor-pointer transition-colors duration-150"
                      >
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-3">
                            <AlertTriangle 
                              size={18} 
                              className={
                                anomaly.severity === "Critical" ? "text-red-500" :
                                anomaly.severity === "Warning" ? "text-yellow-500" : "text-blue-400"
                              } 
                            />
                            <div>
                              <h4 className="font-medium text-gray-200">{anomaly.description}</h4>
                              <div className="flex items-center gap-3 mt-1">
                                <span className="text-xs text-gray-400 flex items-center gap-1">
                                  <Clock size={12} />
                                  {formatDateTime(anomaly.timestamp)}
                                </span>
                                <span className="text-xs text-gray-400">
                                  {anomaly.modelName}
                                </span>
                                <SeverityBadge severity={anomaly.severity} />
                              </div>
                            </div>
                          </div>
                          <ChevronRight size={16} className="text-gray-500" />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
      
      {/* Modal Popup */}
      {showModal && selectedAnomaly && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg w-full max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
            <div className="flex justify-between items-center px-6 py-4 border-b border-gray-700/50">
              <h3 className="font-bold text-lg text-gray-200">Anomaly Details</h3>
              <button 
                onClick={closeModal}
                className="text-gray-400 hover:text-white transition-colors p-1"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <h4 className="text-xs uppercase text-gray-500 mb-1">Timestamp</h4>
                  <p className="text-gray-200 flex items-center gap-2">
                    <Clock size={16} className="text-blue-400" />
                    {formatDateTime(selectedAnomaly.timestamp)}
                  </p>
                </div>
                <div>
                  <h4 className="text-xs uppercase text-gray-500 mb-1">Detection Model</h4>
                  <p className="text-gray-200">{selectedAnomaly.modelName}</p>
                </div>
                <div>
                  <h4 className="text-xs uppercase text-gray-500 mb-1">Severity</h4>
                  <SeverityBadge severity={selectedAnomaly.severity} />
                </div>
              </div>
              
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Description</h4>
                <p className="text-gray-200 bg-gray-700/30 p-3 rounded-md">
                  {selectedAnomaly.description}
                </p>
              </div>
              
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Anomalous Logs</h4>
                <div className="bg-gray-900/70 rounded-md overflow-hidden font-mono text-xs">
                  {selectedAnomaly.anomalousLogs.map((log, index) => (
                    <div 
                      key={index} 
                      className="p-2 border-b border-gray-800 last:border-0"
                    >
                      {log}
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Diagnostic Information</h4>
                <div className="bg-gray-700/30 p-3 rounded-md text-gray-200">
                  {selectedAnomaly.diagnosticInfo}
                </div>
              </div>
            </div>
            
            <div className="px-6 py-4 border-t border-gray-700/50 flex justify-end">
              <button 
                onClick={closeModal}
                className="bg-gray-700 hover:bg-gray-600 text-gray-200 px-4 py-2 rounded-md text-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnomalyDetectionDashboard;