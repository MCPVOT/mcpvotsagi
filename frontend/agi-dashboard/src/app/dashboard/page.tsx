'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Brain, HardDrive, MessageSquare, Zap, Globe, Shield } from 'lucide-react';
import { AnimatedAgentCard } from '@/components/agents/animated-agent-card';
import { AnimatedStorageMonitor } from '@/components/storage/animated-storage-monitor';
import { ChatInterface } from '@/components/chat/chat-interface';
import { ModelOrchestrator } from '@/components/models/model-orchestrator';
import { RealtimeMetrics } from '@/components/metrics/realtime-metrics';
import { agiClient, Agent, StorageStats } from '@/lib/api/agi-client';

export default function DashboardPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [storageStats, setStorageStats] = useState<StorageStats | null>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [wsConnected, setWsConnected] = useState(false);

  // Initialize data fetching
  useEffect(() => {
    // Fetch initial data
    fetchSystemStatus();
    fetchAgents();
    fetchStorageStats();

    // Set up polling
    const interval = setInterval(() => {
      fetchSystemStatus();
      fetchStorageStats();
    }, 5000);

    // Connect WebSocket
    connectWebSocket();

    return () => {
      clearInterval(interval);
      agiClient.disconnect();
    };
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const status = await agiClient.getStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const fetchAgents = async () => {
    try {
      const agentList = await agiClient.getAgents();
      setAgents(agentList);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const fetchStorageStats = async () => {
    try {
      const stats = await agiClient.getStorageStats();
      setStorageStats(stats);
    } catch (error) {
      console.error('Failed to fetch storage stats:', error);
    }
  };

  const connectWebSocket = () => {
    agiClient.connectWebSocket((data) => {
      setWsConnected(true);
      
      // Handle real-time updates
      if (data.type === 'system_status') {
        setSystemStatus(data.data);
      } else if (data.type === 'agent_update') {
        fetchAgents();
      } else if (data.type === 'storage_update') {
        setStorageStats(data.data);
      }
    });
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
            ULTIMATE AGI System V3
          </h1>
          <p className="text-muted-foreground mt-2">
            Advanced AI orchestration with 853GB F: drive intelligence
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={wsConnected ? 'default' : 'secondary'}>
            {wsConnected ? 'Connected' : 'Connecting...'}
          </Badge>
          {systemStatus && (
            <Badge variant="outline">
              v{systemStatus.version}
            </Badge>
          )}
        </div>
      </motion.div>

      {/* System Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{agents.length}</div>
              <p className="text-xs text-muted-foreground">
                {agents.filter(a => a.status === 'online').length} online
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
              <HardDrive className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {storageStats ? `${storageStats.disk_usage.used_gb.toFixed(1)}GB` : '---'}
              </div>
              <p className="text-xs text-muted-foreground">
                of {storageStats ? `${storageStats.disk_usage.total_gb.toFixed(1)}GB` : '853GB'}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {systemStatus?.real_time_metrics?.total_requests || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                All time
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold capitalize">
                {systemStatus?.real_time_metrics?.system_health || 'Unknown'}
              </div>
              <p className="text-xs text-muted-foreground">
                All systems operational
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="storage">Storage</TabsTrigger>
          <TabsTrigger value="models">Models</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <RealtimeMetrics metrics={systemStatus?.real_time_metrics} />
            {storageStats && <AnimatedStorageMonitor stats={storageStats} />}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {agents.slice(0, 3).map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <AnimatedAgentCard agent={agent} />
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="chat" className="space-y-4">
          <ChatInterface />
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <AnimatedAgentCard agent={agent} />
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="storage" className="space-y-4">
          {storageStats && <AnimatedStorageMonitor stats={storageStats} />}
        </TabsContent>

        <TabsContent value="models" className="space-y-4">
          <ModelOrchestrator />
        </TabsContent>
      </Tabs>
    </div>
  );
}