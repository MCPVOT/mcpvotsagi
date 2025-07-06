
"use client";

import { useState, useEffect } from "react";
import { io, Socket } from "socket.io-client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { API_BASE_URL } from "@/lib/config";

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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
                🚀 ULTIMATE AGI SYSTEM V3
              </span>
            </h1>
            <p className="text-gray-300 text-lg">
              Version {dashboardData.version} • Uptime: {Math.floor(dashboardData.uptime / 60)}m
            </p>
          </div>
          <Badge
            variant={connected ? "default" : "destructive"}
            className={`text-lg px-4 py-2 ${connected ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}`}
          >
            {connected ? "🟢 CONNECTED" : "🔴 DISCONNECTED"}
          </Badge>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-700/50 transition-all duration-300 hover:scale-105">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-cyan-400">SYSTEM HEALTH</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">
                {dashboardData.real_time_metrics.system_health.toUpperCase()}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-700/50 transition-all duration-300 hover:scale-105">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-400">ACTIVE MODELS</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400">
                {dashboardData.real_time_metrics.models_loaded}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-700/50 transition-all duration-300 hover:scale-105">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-purple-400">UI COMPONENTS</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-400">
                {dashboardData.ui_components.total_components}
              </div>
              <p className="text-xs text-gray-400 mt-1">
                {dashboardData.ui_components.available_libraries.join(", ")}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-700/50 transition-all duration-300 hover:scale-105">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-yellow-400">CONTEXT TOKENS</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-400">
                {dashboardData.real_time_metrics.context_tokens.toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* UI Components Overview */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-xl text-cyan-400">🎨 INTEGRATED UI COMPONENTS</CardTitle>
            <CardDescription className="text-gray-400">
              Components from cloned repositories ready for use
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 border border-gray-700 rounded-lg bg-gradient-to-br from-blue-900/20 to-blue-800/20 hover:from-blue-900/30 hover:to-blue-800/30 transition-all duration-300">
                <div className="text-3xl font-bold text-blue-400 mb-2">
                  {dashboardData.ui_components.animate_ui_components}
                </div>
                <p className="text-sm text-gray-400">Animate UI Components</p>
              </div>
              <div className="text-center p-6 border border-gray-700 rounded-lg bg-gradient-to-br from-green-900/20 to-green-800/20 hover:from-green-900/30 hover:to-green-800/30 transition-all duration-300">
                <div className="text-3xl font-bold text-green-400 mb-2">
                  {dashboardData.ui_components.dashboard_components}
                </div>
                <p className="text-sm text-gray-400">Dashboard Components</p>
              </div>
              <div className="text-center p-6 border border-gray-700 rounded-lg bg-gradient-to-br from-purple-900/20 to-purple-800/20 hover:from-purple-900/30 hover:to-purple-800/30 transition-all duration-300">
                <div className="text-3xl font-bold text-purple-400 mb-2">
                  {dashboardData.ui_components.available_icons}
                </div>
                <p className="text-sm text-gray-400">Available Icons</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agents Overview */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-xl text-cyan-400">🤖 ACTIVE AGENTS</CardTitle>
            <CardDescription className="text-gray-400">
              {dashboardData.agents.length} agents ready for execution
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboardData.agents.slice(0, 5).map((agent, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-gray-700 rounded-lg bg-gradient-to-r from-gray-800/50 to-gray-700/50 hover:from-gray-700/50 hover:to-gray-600/50 transition-all duration-300">
                  <span className="font-medium text-white">{agent.name || `Agent ${index + 1}`}</span>
                  <Badge className="bg-green-600 hover:bg-green-700 text-white">READY</Badge>
                </div>
              ))}
              {dashboardData.agents.length > 5 && (
                <div className="text-center p-3 border border-gray-700 rounded-lg bg-gradient-to-r from-gray-800/50 to-gray-700/50">
                  <span className="text-gray-400">+{dashboardData.agents.length - 5} more agents available</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
