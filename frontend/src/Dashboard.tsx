import { useState, useEffect } from "react";
import { Home, AlertTriangle, BarChart2, PieChart, Settings } from "lucide-react";
import { BrowserRouter, Routes, Route, NavLink as RouterNavLink, Navigate } from "react-router-dom";
import HomePage from "./pages/Home";
import Anomalies from "./pages/Anomalies";
import Model1 from "./pages/Model-1";
import Model2 from "./pages/Model-2";
import Configuration from "./pages/Settings";

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
              group-hover:scale-90
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

export default function Dashboard() {
  const [isNavExpanded, setIsNavExpanded] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-black text-white">
        <header className="p-6 bg-gray-900/80 backdrop-blur-sm fixed top-0 left-0 right-0 z-20 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-300">📊 Monitoring Dashboard</h1>
          <div className="flex items-center gap-3">
            {/* <button className="flex items-center gap-1 text-xs text-gray-400 bg-gray-700/80 rounded-full px-3 py-1">
              <Clock size={14} />
              <span>24 hours</span>
            </button> */}
            {/* <button className="flex items-center gap-1 text-xs text-gray-400 bg-gray-700/80 rounded-full px-3 py-1">
              <Share size={14} />
              <span>Share</span>
            </button> */}
            {/* <button className="flex items-center gap-1 text-xs text-gray-400 bg-gray-700/80 rounded-full px-3 py-1">
              <Edit size={14} />
              <span>Edit</span>
            </button> */}
            {/* <button className="text-gray-400 hover:text-white">
              <MoreVertical size={18} />
            </button> */}
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
                ? 'w-32 bg-gray-900/70 backdrop-blur-sm'
                : 'w-14 bg-gray-900/60'} 
              overflow-hidden
            `}
            onMouseEnter={() => setIsNavExpanded(true)}
            onMouseLeave={() => setIsNavExpanded(false)}
          >
            <div className="flex flex-col space-y-2 px-1 py-2">
              <NavItem to="/" icon={Home}>
                Home
              </NavItem>
              <NavItem to="/anomalies" icon={AlertTriangle}>
                Anomalies
              </NavItem>
              <NavItem to="/model1" icon={BarChart2}>
                Model1
              </NavItem>
              <NavItem to="/model2" icon={PieChart}>
                Model2
              </NavItem>
              <NavItem to="/config" icon={Settings}>
                Config
              </NavItem>
            </div>
          </nav>
          {/* Main content area with fixed left margin */}
          <main className="flex-1 p-6 overflow-y-auto min-h-screen ml-14">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/anomalies" element={<Anomalies />} />
              <Route path="/model1" element={<Model1 />} />
              <Route path="/model2" element={<Model2 />} />
              <Route path="/config" element={<Configuration />} />
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
          
          /* Card styling for components */
          .dashboard-card {
            background-color: rgba(31, 41, 55, 0.7);
            border-radius: 0.5rem;
            overflow: hidden;
            border: 1px solid rgba(55, 65, 81, 0.3);
            margin-bottom: 1rem;
          }
          
          .dashboard-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid rgba(75, 85, 99, 0.3);
          }
          
          .dashboard-card-title {
            font-size: 0.875rem;
            font-weight: 500;
            color: #d1d5db;
          }
          
          .dashboard-card-content {
            padding: 1rem;
          }
          
          /* Chart containers */
          .chart-container {
            height: 15rem;
            width: 100%;
          }
          
          /* Progress indicators */
          .circular-indicator {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
          }
          
          .circular-indicator-value {
            font-size: 4rem;
            font-weight: bold;
            color: #60a5fa;
          }
          
          /* Status indicators */
          .status-dot {
            display: inline-block;
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 9999px;
            margin-right: 0.5rem;
          }
          
          .status-dot.active {
            background-color: #10b981;
          }
          
          /* Time badge */
          .time-badge {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.75rem;
            color: #9ca3af;
            background-color: rgba(55, 65, 81, 0.5);
            border-radius: 9999px;
            padding: 0.25rem 0.75rem;
          }
          
          /* Grid layout for dashboard */
          .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(12, minmax(0, 1fr));
            gap: 1rem;
          }
          
          @media (min-width: 768px) {
            .dashboard-col-6 {
              grid-column: span 6 / span 6;
            }
            
            .dashboard-col-3 {
              grid-column: span 3 / span 3;
            }
            
            .dashboard-col-12 {
              grid-column: span 12 / span 12;
            }
          }
          
          /* Large metrics */
          .large-metric {
            font-size: 5rem;
            font-weight: bold;
            text-align: center;
          }
          
          .large-metric.success {
            color: #10b981;
          }
          
          .large-metric.info {
            color: #60a5fa;
          }
        `}</style>
      </div>
    </BrowserRouter>
  );
}