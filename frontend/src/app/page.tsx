
"use client";

import { useState, useEffect } from "react";
import { io, Socket } from "socket.io-client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { API_BASE_URL } from "@/lib/config";
import { ChatInterface } from "@/components/chat/chat-interface";

interface SystemMetrics {
  system_health: string;
  active_sessions: number;
  total_requests: number;
  models_loaded: number;
  context_tokens: number;
  learning_progress: number;
}

interface DashboardData {
  version: string;
  uptime: number;
  agents: Array<{
    id: string;
    name: string;
    status: string;
    [key: string]: unknown;
  }>;
  ui_components: {
    total_components: number;
    available_libraries: string[];
    animate_ui_components: number;
    dashboard_components: number;
    available_icons: number;
  };
  real_time_metrics: SystemMetrics;
}

export default function UltimateAGIDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to backend
    fetchDashboardData();
    connectWebSocket();
  }, []);

  useEffect(() => {
    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [socket]);

  const fetchDashboardData = async () => {
    try {
      console.log('Fetching dashboard data from:', `${API_BASE_URL}/api/v3/dashboard`);
      console.log('API_BASE_URL value:', API_BASE_URL);
      console.log('process.env.NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);

      const response = await fetch(`${API_BASE_URL}/api/v3/dashboard`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'same-origin',
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error text:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, text: ${errorText}`);
      }

      const data = await response.json();
      console.log('Dashboard data received:', data);
      setDashboardData(data);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      console.error("Error type:", error instanceof Error ? error.constructor.name : typeof error);
      console.error("Error message:", error instanceof Error ? error.message : String(error));
      console.error("API_BASE_URL:", API_BASE_URL);

      // Try fallback to test if backend is reachable
      try {
        console.log('Trying fallback to /api/status...');
        const statusResponse = await fetch(`${API_BASE_URL}/api/status`, {
          mode: 'cors',
          credentials: 'same-origin',
        });
        console.log('Status response status:', statusResponse.status);
        if (statusResponse.ok) {
          const statusData = await statusResponse.text();
          console.log('Backend is reachable via /api/status:', statusData);
        }
      } catch (statusError) {
        console.error('Backend not reachable via /api/status:', statusError);
      }
    }
  };

  const connectWebSocket = () => {
    const ws = io(API_BASE_URL, {
      path: "/ws/v3/realtime"
    });

    ws.on("connect", () => {
      setConnected(true);
      console.log("Connected to ULTIMATE AGI SYSTEM V3");
    });

    ws.on("disconnect", () => {
      setConnected(false);
      console.log("Disconnected from ULTIMATE AGI SYSTEM V3");
    });

    ws.on("metrics", (data) => {
      setDashboardData(prev => prev ? {...prev, real_time_metrics: data.data} : null);
    });

    setSocket(ws);
  };

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-8">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 animate-pulse">
              🚀 ULTIMATE AGI SYSTEM V3
            </span>
          </h1>
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-600 border-t-cyan-400 mx-auto mb-4"></div>
            <div className="absolute inset-0 animate-ping rounded-full h-16 w-16 border-2 border-cyan-400 opacity-20 mx-auto"></div>
          </div>
          <p className="text-gray-400 text-lg animate-pulse">
            Initializing Neural Networks...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      <div className="h-screen flex flex-col">
        {/* Header */}
        <div className="bg-gray-900/50 backdrop-blur-lg border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 animate-gradient">
                  🚀 ULTIMATE AGI SYSTEM V3
                </span>
              </h1>
              <p className="text-gray-400 text-sm">
                Version {dashboardData.version} • Uptime: {Math.floor(dashboardData.uptime / 60)}m
              </p>
            </div>
            <Badge
              variant={connected ? "default" : "destructive"}
              className={`text-sm px-3 py-1 ${connected ? 'bg-green-600/20 text-green-400 border-green-500' : 'bg-red-600/20 text-red-400 border-red-500'}`}
            >
              {connected ? "● Connected" : "● Disconnected"}
            </Badge>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar - Agents & Metrics */}
          <div className="w-80 bg-gray-900/30 border-r border-gray-700 p-4 overflow-y-auto">
            {/* Quick Metrics */}
            <div className="space-y-3 mb-6">
              <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">System Health</span>
                  <span className="text-sm font-bold text-green-400">
                    {dashboardData?.real_time_metrics?.system_health?.toUpperCase() || "OPERATIONAL"}
                  </span>
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">Active Models</span>
                  <span className="text-sm font-bold text-blue-400">
                    {dashboardData?.real_time_metrics?.models_loaded || 3}
                  </span>
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">Context Tokens</span>
                  <span className="text-sm font-bold text-yellow-400">
                    {dashboardData?.real_time_metrics?.context_tokens?.toLocaleString() || "128,000"}
                  </span>
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">Learning Progress</span>
                  <span className="text-sm font-bold text-purple-400">
                    {dashboardData?.real_time_metrics?.learning_progress || 75}%
                  </span>
                </div>
              </div>
            </div>

            {/* Active Agents */}
            <div>
              <h3 className="text-sm font-semibold text-gray-300 mb-3">ACTIVE AGENTS</h3>
              <div className="space-y-2">
                {dashboardData?.agents?.map((agent, index) => (
                  <div 
                    key={index} 
                    className="bg-gray-800/30 rounded-lg p-3 border border-gray-700 hover:bg-gray-800/50 transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-white">{agent.name}</p>
                        <p className="text-xs text-gray-400">{agent.id}</p>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-400' : 'bg-yellow-400'} animate-pulse`}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Chat Interface with Analysis */}
          <div className="flex-1 flex flex-col bg-gray-900/20">
            <div className="flex-1">
              <ChatInterface />
            </div>
            
            {/* Analysis Controls */}
            <div className="border-t border-gray-700 p-4 bg-gray-900/30">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">CODEBASE ANALYSIS</h3>
              <div className="space-y-2">
                <button
                  onClick={async () => {
                    const paths = ["/app/data"];
                    const response = await fetch('http://localhost:8889/api/v3/analyze', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ paths, include_github: true })
                    });
                    const result = await response.json();
                    console.log('Analysis result:', result);
                    alert(`Analyzed ${result.total_files} files in ${result.analyzed_paths.length} repositories!`);
                  }}
                  className="w-full bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors"
                >
                  Analyze MCPVotsAGI Codebase
                </button>
                
                <button
                  onClick={async () => {
                    const response = await fetch('http://localhost:8889/api/v3/upgrade-plan');
                    const plan = await response.json();
                    console.log('Upgrade plan:', plan);
                    alert(`Upgrade Plan Ready!\n\nTop Recommendations:\n${plan.recommendations.slice(0,3).map(r => `- ${r.title}`).join('\n')}`);
                  }}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors"
                >
                  Get Upgrade Plan
                </button>
              </div>
            </div>
          </div>

          {/* Right Sidebar - Additional Info */}
          <div className="w-64 bg-gray-900/30 border-l border-gray-700 p-4 overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">UI COMPONENTS</h3>
            <div className="space-y-3">
              <div className="text-center p-4 bg-gradient-to-br from-blue-900/20 to-blue-800/20 rounded-lg border border-blue-800/30">
                <div className="text-2xl font-bold text-blue-400">
                  {dashboardData?.ui_components?.animate_ui_components || 45}
                </div>
                <p className="text-xs text-gray-400">Animate UI</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-green-900/20 to-green-800/20 rounded-lg border border-green-800/30">
                <div className="text-2xl font-bold text-green-400">
                  {dashboardData?.ui_components?.dashboard_components || 25}
                </div>
                <p className="text-xs text-gray-400">Dashboard</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-purple-900/20 to-purple-800/20 rounded-lg border border-purple-800/30">
                <div className="text-2xl font-bold text-purple-400">
                  {dashboardData?.ui_components?.available_icons || 300}
                </div>
                <p className="text-xs text-gray-400">Icons</p>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">LIBRARIES</h3>
              <div className="space-y-2">
                {dashboardData?.ui_components?.available_libraries?.map((lib, index) => (
                  <div key={index} className="text-xs text-gray-400 bg-gray-800/30 rounded px-2 py-1">
                    {lib}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
