import { useState, useEffect } from "react";
import { Home, AlertTriangle, BarChart2, PieChart, Settings, Clock, Share, Edit, MoreVertical } from "lucide-react";
import { BrowserRouter, Routes, Route, NavLink as RouterNavLink, Navigate } from "react-router-dom";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// Dummy data for charts
const processorData = Array.from({ length: 12 }, (_, i) => ({
  time: `${11 + Math.floor(i/4)}:${(i % 4) * 5 + 20}`,
  cpu1: Math.random() * 10 + 5,
  cpu2: Math.random() * 5 + 3,
  cpu3: Math.random() * 4 + 1,
  cpu4: Math.random() * 6 + 2,
  main: Math.random() * 5 + 10,
}));

const diskData = [
  { name: "C:\\System", value: 65 },
  { name: "D:\\Program", value: 72 },
  { name: "E:\\UserData", value: 58 },
  { name: "F:\\Temp", value: 69 },
  { name: "G:\\Backup", value: 75 },
];

const requestsData = Array.from({ length: 24 }, (_, i) => ({
  time: `${11}:${30 + i}`,
  requests: 500 + Math.random() * 500,
}));
// Spike at 11:43
requestsData[13] = { ...requestsData[13], requests: 2000 };

function NavItem({ to, icon: Icon, children }) {
  return (
    <RouterNavLink
      to={to}
      className={({ isActive }) => `
        group p-2 rounded-lg w-full
        flex items-center gap-2
        transition-all duration-200
        ${isActive
          ? 'bg-gray-700/70 text-blue-400'
          : 'text-gray-300 hover:text-white hover:bg-gray-700/40'}
      `}
    >
      {({ isActive }) => (
        <>
          <Icon
            size={20}
            className={`
              transition-all duration-200
              ${isActive ? 'text-blue-400' : 'group-hover:text-white'}
            `}
          />
          <span className="nav-text text-sm whitespace-nowrap">
            {children}
          </span>
        </>
      )}
    </RouterNavLink>
  );
}

// Circular Progress Component
function CircularProgress({ value, total, label, size = "lg", color = "blue" }) {
  const percentage = (value / total) * 100;
  const radius = size === "lg" ? 50 : 40;
  const strokeWidth = size === "lg" ? 8 : 6;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  const colorClasses = {
    blue: "text-blue-400",
    green: "text-green-500",
  };
  
  return (
    <div className="relative flex items-center justify-center">
      <svg width={radius * 2.5} height={radius * 2.5} className="transform -rotate-90">
        <circle
          cx={radius * 1.25}
          cy={radius * 1.25}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-gray-700"
        />
        <circle
          cx={radius * 1.25}
          cy={radius * 1.25}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className={colorClasses[color]}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className={`font-bold ${size === "lg" ? "text-5xl" : "text-3xl"} ${colorClasses[color]}`}>
          {value}
        </span>
        {label && <span className="text-gray-400 text-sm mt-1">{label}</span>}
      </div>
    </div>
  );
}

// Card component
function Card({ title, children, className = "", headerRight = null, timeDisplay = "24 hours" }) {
  return (
    <div className={`bg-gray-800/70 rounded-lg overflow-hidden ${className}`}>
      {title && (
        <div className="flex justify-between items-center px-4 py-2 border-b border-gray-700/50">
          <h3 className="font-medium text-gray-300">{title}</h3>
          <div className="flex items-center gap-2">
            {timeDisplay && (
              <div className="flex items-center gap-1 text-xs text-gray-400 bg-gray-700/50 rounded-full px-2 py-1">
                <Clock size={12} />
                <span>{timeDisplay}</span>
              </div>
            )}
            {headerRight}
          </div>
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}

// Main Dashboard Component
function LogAnalyticsDashboard() {
  return (
    <div className="grid grid-cols-12 gap-4">
      <div className="col-span-12 flex justify-between items-center mb-2">
        <h2 className="text-xl font-bold flex items-center">
          <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
          Log Analytics
        </h2>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-1 text-xs text-gray-400 bg-gray-700/80 rounded-full px-3 py-1">
            <Clock size={14} />
            <span>24 hours</span>
          </button>
          <button className="flex items-center gap-1 text-xs text-gray-400 bg-gray-700/80 rounded-full px-3 py-1">
            <Share size={14} />
            <span>Share</span>
          </button>
          <button className="flex items-center gap-1 text-xs text-gray-400 bg-gray-700/80 rounded-full px-3 py-1">
            <Edit size={14} />
            <span>Edit</span>
          </button>
          <button className="text-gray-400 hover:text-white">
            <MoreVertical size={18} />
          </button>
        </div>
      </div>

      {/* CPU Utilization Chart */}
      <div className="col-span-12 md:col-span-8 lg:col-span-6">
        <Card title="Processor Utilization VM Insights">
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={processorData}>
                <Line type="monotone" dataKey="main" stroke="#8884d8" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="cpu1" stroke="#82ca9d" strokeWidth={1} dot={false} />
                <Line type="monotone" dataKey="cpu2" stroke="#ffc658" strokeWidth={1} dot={false} />
                <Line type="monotone" dataKey="cpu3" stroke="#ff8042" strokeWidth={1} dot={false} />
                <Line type="monotone" dataKey="cpu4" stroke="#0088fe" strokeWidth={1} dot={false} />
                <XAxis dataKey="time" stroke="#6b7280" fontSize={10} />
                <YAxis stroke="#6b7280" fontSize={10} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    borderColor: '#374151',
                    color: '#e5e7eb'
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Disk VM Insights */}
      <div className="col-span-12 md:col-span-4 lg:col-span-6">
        <Card title="Disk % VM Insights">
          <div className="h-60 flex items-center justify-center">
            <BarChart width={400} height={200} data={diskData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis dataKey="name" type="category" width={100} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  borderColor: '#374151',
                  color: '#e5e7eb'
                }}
              />
              <Bar dataKey="value" fill="#4f46e5" barSize={20} radius={[0, 4, 4, 0]} />
            </BarChart>
          </div>
        </Card>
      </div>

      {/* AAD Operations */}
      <div className="col-span-12 md:col-span-4 lg:col-span-3">
        <Card title="AADOperations By Type Sentinel">
          <div className="h-48 flex items-center justify-center">
            <CircularProgress value={77} total={100} size="lg" />
          </div>
          <div className="flex justify-center gap-6 mt-2">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-blue-500 rounded-sm"></div>
              <span className="text-xs text-gray-300">Update</span>
              <span className="text-xs text-gray-400 ml-1">73</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 rounded-sm"></div>
              <span className="text-xs text-gray-300">Add</span>
              <span className="text-xs text-gray-400 ml-1">2</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-purple-500 rounded-sm"></div>
              <span className="text-xs text-gray-300">Assign</span>
              <span className="text-xs text-gray-400 ml-1">2</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Sign ins by location */}
      <div className="col-span-12 md:col-span-4 lg:col-span-3">
        <Card title="Sign ins by Location">
          <div className="flex items-center justify-center h-48">
            <CircularProgress value={46} total={100} size="lg" />
          </div>
          <div className="grid grid-cols-3 gap-2 mt-2 text-xs text-center">
            <div className="text-blue-400">
              <div>IND</div>
              <div>55.00</div>
            </div>
            <div className="text-blue-400">
              <div>GB</div>
              <div>31.00</div>
            </div>
            <div className="text-blue-400">
              <div>US</div>
              <div>15.00</div>
            </div>
          </div>
        </Card>
      </div>

      {/* SquaredUp Logo */}
      <div className="col-span-12 md:col-span-4 lg:col-span-3 flex items-center justify-center">
        <div className="bg-transparent p-8">
          <div className="flex items-center justify-center mb-2">
            <div className="w-10 h-10 bg-red-500 flex items-center justify-center rounded mr-2">
              <div className="w-6 h-6 border-2 border-white"></div>
            </div>
            <span className="text-2xl font-bold">SquaredUp</span>
          </div>
        </div>
      </div>

      {/* App Exceptions */}
      <div className="col-span-12 md:col-span-4 lg:col-span-3">
        <Card title="App Exceptions" timeDisplay="24 hours" className="flex flex-col">
          <div className="flex-1 flex items-center justify-center">
            <div className="text-green-500 text-8xl font-bold">25</div>
          </div>
        </Card>
      </div>

      {/* App Requests Last Hour */}
      <div className="col-span-12">
        <Card title="App Requests Last Hour App Insights">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={requestsData}>
                <Line 
                  type="monotone" 
                  dataKey="requests" 
                  stroke="#3b82f6" 
                  strokeWidth={2} 
                  dot={false}
                  activeDot={{ r: 8 }}
                  fill="url(#colorGradient)"
                />
                <XAxis dataKey="time" stroke="#6b7280" fontSize={10} />
                <YAxis stroke="#6b7280" fontSize={10} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    borderColor: '#374151',
                    color: '#e5e7eb'
                  }}
                />
                <defs>
                  <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#374151" strokeDasharray="3 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [isNavExpanded, setIsNavExpanded] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-black text-white">
        <header className="p-6 bg-gray-900/80 backdrop-blur-sm fixed top-0 left-0 right-0 z-20 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-300">📊 Monitoring Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">Last updated: 10:25 AM</span>
            <div className="w-8 h-8 bg-blue-500 rounded-full"></div>
          </div>
        </header>
       
        <div className="flex pt-20">
          {/* Transparent navigation sidebar when hovered */}
          <nav
            className={`
              fixed left-0 top-20 z-10
              h-screen
              transition-all duration-300 ease-in-out
              ${isNavExpanded
                ? 'w-48 bg-gray-900/70 backdrop-blur-sm'
                : 'w-16 bg-gray-900/60'} 
              overflow-hidden
            `}
            onMouseEnter={() => setIsNavExpanded(true)}
            onMouseLeave={() => setIsNavExpanded(false)}
          >
            <div className="flex flex-col space-y-1 px-2 py-4">
              <NavItem to="/" icon={Home}>
                Dashboard
              </NavItem>
              <NavItem to="/anomalies" icon={AlertTriangle}>
                Anomalies
              </NavItem>
              <NavItem to="/model1" icon={BarChart2}>
                Performance
              </NavItem>
              <NavItem to="/model2" icon={PieChart}>
                Resources
              </NavItem>
              <NavItem to="/config" icon={Settings}>
                Settings
              </NavItem>
            </div>
          </nav>
          
          {/* Main content area with fixed left margin */}
          <main className={`flex-1 p-6 overflow-y-auto min-h-screen transition-all duration-300 ${isNavExpanded ? 'ml-48' : 'ml-16'}`}>
            <Routes>
              <Route path="/" element={<LogAnalyticsDashboard />} />
              <Route path="/anomalies" element={<div>Anomalies Page</div>} />
              <Route path="/model1" element={<div>Performance Monitoring</div>} />
              <Route path="/model2" element={<div>Resource Allocation</div>} />
              <Route path="/config" element={<div>Settings Page</div>} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
        
        <style>{`
          .nav-text {
            opacity: ${isNavExpanded ? 1 : 0};
            transition: opacity 0.3s;
            ${!isNavExpanded ? 'width: 0;' : ''}
          }
        `}</style>
      </div>
    </BrowserRouter>
  );
}