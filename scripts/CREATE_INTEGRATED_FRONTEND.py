#!/usr/bin/env python3
"""
Frontend Integration Generator - Uses Cloned Repositories
========================================================
Creates a complete frontend integration using:
- animate-ui components for animations
- next-shadcn-dashboard-starter for professional UI
- icons for comprehensive icon library
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List

def create_integrated_frontend():
    """Create integrated frontend using cloned repositories"""

    # Paths
    workspace_root = Path(__file__).parent
    frontend_dir = workspace_root / "frontend"
    external_libs = frontend_dir / "external-libs"

    # Create frontend structure
    frontend_dir.mkdir(exist_ok=True)
    (frontend_dir / "src").mkdir(exist_ok=True)
    (frontend_dir / "src" / "components").mkdir(exist_ok=True)
    (frontend_dir / "src" / "pages").mkdir(exist_ok=True)
    (frontend_dir / "src" / "lib").mkdir(exist_ok=True)
    (frontend_dir / "src" / "hooks").mkdir(exist_ok=True)

    print("🎨 Creating integrated frontend from cloned repositories...")

    # 1. Create package.json integrating all dependencies
    create_integrated_package_json(frontend_dir, external_libs)

    # 2. Create main dashboard component using dashboard-starter
    create_main_dashboard(frontend_dir, external_libs)

    # 3. Create animated components using animate-ui
    create_animated_components(frontend_dir, external_libs)

    # 4. Create icon integration
    create_icon_integration(frontend_dir, external_libs)

    # 5. Create API integration
    create_api_integration(frontend_dir)

    # 6. Create configuration files
    create_config_files(frontend_dir, external_libs)

    print("✅ Integrated frontend created successfully!")
    print(f"📁 Frontend location: {frontend_dir}")
    print("🚀 Run 'npm install && npm run dev' to start development")

def create_integrated_package_json(frontend_dir: Path, external_libs: Path):
    """Create package.json integrating all repositories"""

    # Read package.json from dashboard starter
    dashboard_pkg_path = external_libs / "next-shadcn-dashboard-starter" / "package.json"
    animate_pkg_path = external_libs / "animate-ui" / "package.json"

    base_package = {
        "name": "ultimate-agi-system-v3-frontend",
        "version": "3.0.0",
        "description": "Ultimate AGI System V3 - Modern Frontend with Animations",
        "private": True
    }

    if dashboard_pkg_path.exists():
        with open(dashboard_pkg_path, 'r') as f:
            dashboard_pkg = json.load(f)

        # Merge dependencies
        base_package.update({
            "scripts": dashboard_pkg.get("scripts", {}),
            "dependencies": dashboard_pkg.get("dependencies", {}),
            "devDependencies": dashboard_pkg.get("devDependencies", {})
        })

    # Add animate-ui dependencies if available
    if animate_pkg_path.exists():
        with open(animate_pkg_path, 'r') as f:
            animate_pkg = json.load(f)

        # Merge animation dependencies
        base_package["dependencies"].update({
            "framer-motion": "^11.0.0",
            "@radix-ui/react-slot": "^1.0.0",
            "lucide-react": "^0.400.0"
        })

    # Add our specific dependencies
    base_package["dependencies"].update({
        "socket.io-client": "^4.7.0",
        "recharts": "^2.8.0",
        "react-hook-form": "^7.48.0",
        "@hookform/resolvers": "^3.3.0",
        "zod": "^3.22.0"
    })

    # Update scripts for our setup
    base_package["scripts"].update({
        "dev": "next dev -p 3000",
        "build": "next build",
        "start": "next start -p 3000",
        "preview": "next start",
        "integrate": "python ../src/core/ULTIMATE_AGI_SYSTEM_V3.py"
    })

    with open(frontend_dir / "package.json", 'w', encoding='utf-8') as f:
        json.dump(base_package, f, indent=2)

    print("  ✓ Created integrated package.json")

def create_main_dashboard(frontend_dir: Path, external_libs: Path):
    """Create main dashboard using dashboard-starter as base"""

    dashboard_src = external_libs / "next-shadcn-dashboard-starter" / "src"

    if dashboard_src.exists():
        # Copy dashboard components
        src_components = dashboard_src / "components"
        dest_components = frontend_dir / "src" / "components"

        if src_components.exists():
            shutil.copytree(src_components, dest_components, dirs_exist_ok=True)

        # Copy app structure
        src_app = dashboard_src / "app"
        dest_app = frontend_dir / "src" / "app"

        if src_app.exists():
            shutil.copytree(src_app, dest_app, dirs_exist_ok=True)

    # Create enhanced main page
    main_page_content = '''
"use client";

import { useState, useEffect } from "react";
import { io, Socket } from "socket.io-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

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
  agents: any[];
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

    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch("http://localhost:8889/api/v3/dashboard");
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    }
  };

  const connectWebSocket = () => {
    const ws = io("ws://localhost:8889", {
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
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Loading ULTIMATE AGI SYSTEM V3...</h1>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              🚀 ULTIMATE AGI SYSTEM V3
            </h1>
            <p className="text-muted-foreground">
              Version {dashboardData.version} • Uptime: {Math.floor(dashboardData.uptime / 60)}m
            </p>
          </div>
          <Badge variant={connected ? "default" : "destructive"}>
            {connected ? "🟢 Connected" : "🔴 Disconnected"}
          </Badge>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {dashboardData.real_time_metrics.system_health.toUpperCase()}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Active Models</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dashboardData.real_time_metrics.models_loaded}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">UI Components</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {dashboardData.ui_components.total_components}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.ui_components.available_libraries.join(", ")}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Context Tokens</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {dashboardData.real_time_metrics.context_tokens.toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* UI Components Overview */}
        <Card>
          <CardHeader>
            <CardTitle>🎨 Integrated UI Components</CardTitle>
            <CardDescription>
              Components from cloned repositories ready for use
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {dashboardData.ui_components.animate_ui_components}
                </div>
                <p className="text-sm text-muted-foreground">Animate UI Components</p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {dashboardData.ui_components.dashboard_components}
                </div>
                <p className="text-sm text-muted-foreground">Dashboard Components</p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {dashboardData.ui_components.available_icons}
                </div>
                <p className="text-sm text-muted-foreground">Available Icons</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agents Overview */}
        <Card>
          <CardHeader>
            <CardTitle>🤖 Active Agents</CardTitle>
            <CardDescription>
              {dashboardData.agents.length} agents ready for execution
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {dashboardData.agents.slice(0, 5).map((agent, index) => (
                <div key={index} className="flex items-center justify-between p-2 border rounded">
                  <span className="font-medium">{agent.name || `Agent ${index + 1}`}</span>
                  <Badge>Ready</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
'''

    # Write the main page
    page_path = frontend_dir / "src" / "app" / "page.tsx"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(main_page_content)

    print("  ✓ Created main dashboard with real integration")

def create_animated_components(frontend_dir: Path, external_libs: Path):
    """Create animated components using animate-ui"""

    animate_ui_src = external_libs / "animate-ui" / "packages" / "ui" / "src"

    if animate_ui_src.exists():
        # Copy animate-ui components
        src_components = animate_ui_src / "components"
        dest_animated = frontend_dir / "src" / "components" / "animated"

        if src_components.exists():
            dest_animated.mkdir(parents=True, exist_ok=True)

            # Copy specific animation components
            for component_dir in src_components.iterdir():
                if component_dir.is_dir():
                    shutil.copytree(component_dir, dest_animated / component_dir.name, dirs_exist_ok=True)

    print("  ✓ Integrated animate-ui components")

def create_icon_integration(frontend_dir: Path, external_libs: Path):
    """Create icon integration"""

    icons_src = external_libs / "icons"

    if icons_src.exists():
        # Copy icons to public directory
        public_icons = frontend_dir / "public" / "icons"
        public_icons.mkdir(parents=True, exist_ok=True)

        # Copy SVG icons
        for icon_file in icons_src.rglob("*.svg"):
            dest_file = public_icons / icon_file.name
            shutil.copy2(icon_file, dest_file)

    # Create icon component
    icon_component = '''
import { FC } from "react";

interface IconProps {
  name: string;
  size?: number;
  className?: string;
}

export const Icon: FC<IconProps> = ({ name, size = 24, className = "" }) => {
  return (
    <img
      src={`/icons/${name}.svg`}
      alt={name}
      width={size}
      height={size}
      className={className}
    />
  );
};

export default Icon;
'''

    icon_path = frontend_dir / "src" / "components" / "ui" / "icon.tsx"
    icon_path.parent.mkdir(parents=True, exist_ok=True)
    with open(icon_path, 'w', encoding='utf-8') as f:
        f.write(icon_component)

    print("  ✓ Created icon integration")

def create_api_integration(frontend_dir: Path):
    """Create API integration client"""

    api_client = '''
class UltimateAGIAPI {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8889") {
    this.baseUrl = baseUrl;
  }

  async getDashboard() {
    const response = await fetch(`${this.baseUrl}/api/v3/dashboard`);
    return response.json();
  }

  async getMetrics() {
    const response = await fetch(`${this.baseUrl}/api/v3/metrics`);
    return response.json();
  }

  async getUIComponents() {
    const response = await fetch(`${this.baseUrl}/api/v3/ui/catalog`);
    return response.json();
  }

  async getIcons() {
    const response = await fetch(`${this.baseUrl}/api/v3/ui/icons`);
    return response.json();
  }

  async sendChat(message: string, model?: string, useClaudia?: boolean, agent?: string) {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        model,
        use_claudia: useClaudia,
        agent
      })
    });
    return response.json();
  }

  async executeAgent(agent: string, task: string, context: any = {}) {
    const response = await fetch(`${this.baseUrl}/api/v3/agent/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent, task, context })
    });
    return response.json();
  }
}

export const agiAPI = new UltimateAGIAPI();
export default UltimateAGIAPI;
'''

    api_path = frontend_dir / "src" / "lib" / "api.ts"
    api_path.parent.mkdir(parents=True, exist_ok=True)
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(api_client)

    print("  ✓ Created API integration client")

def create_config_files(frontend_dir: Path, external_libs: Path):
    """Create configuration files"""

    # Copy config from dashboard starter
    dashboard_config = external_libs / "next-shadcn-dashboard-starter"

    config_files = [
        "next.config.ts",
        "tailwind.config.js",
        "components.json",
        "tsconfig.json"
    ]

    for config_file in config_files:
        src_file = dashboard_config / config_file
        if src_file.exists():
            shutil.copy2(src_file, frontend_dir / config_file)

    print("  ✓ Created configuration files")

if __name__ == "__main__":
    create_integrated_frontend()
