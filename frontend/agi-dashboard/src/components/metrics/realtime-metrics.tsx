'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  Cpu,
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface Metrics {
  system_health: string;
  active_sessions: number;
  total_requests: number;
  models_loaded: number;
  context_tokens: number;
  learning_progress: number;
}

interface RealtimeMetricsProps {
  metrics?: Metrics;
}

export function RealtimeMetrics({ metrics }: RealtimeMetricsProps) {
  const [animatedProgress, setAnimatedProgress] = useState(0);

  useEffect(() => {
    if (metrics?.learning_progress) {
      const timer = setTimeout(() => {
        setAnimatedProgress(metrics.learning_progress * 100);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [metrics?.learning_progress]);

  const getHealthColor = (health: string) => {
    switch (health?.toLowerCase()) {
      case 'excellent':
        return 'text-green-500';
      case 'good':
        return 'text-blue-500';
      case 'fair':
        return 'text-yellow-500';
      case 'poor':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health?.toLowerCase()) {
      case 'excellent':
      case 'good':
        return <CheckCircle className="w-4 h-4" />;
      case 'fair':
      case 'poor':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Real-time System Metrics
            </CardTitle>
            <CardDescription>
              Live performance and usage statistics
            </CardDescription>
          </div>
          <Badge variant="outline" className="animate-pulse">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Live
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* System Health */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={getHealthColor(metrics?.system_health || '')}>
              {getHealthIcon(metrics?.system_health || '')}
            </div>
            <span className="text-sm font-medium">System Health</span>
          </div>
          <Badge className={`capitalize ${
            metrics?.system_health === 'excellent' ? 'bg-green-500' : ''
          }`}>
            {metrics?.system_health || 'Unknown'}
          </Badge>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="space-y-2"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Users className="w-4 h-4" />
              Active Sessions
            </div>
            <p className="text-2xl font-bold">
              {metrics?.active_sessions || 0}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-2"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <TrendingUp className="w-4 h-4" />
              Total Requests
            </div>
            <p className="text-2xl font-bold">
              {metrics?.total_requests?.toLocaleString() || 0}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-2"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Cpu className="w-4 h-4" />
              Models Loaded
            </div>
            <p className="text-2xl font-bold">
              {metrics?.models_loaded || 0}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-2"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              Context Tokens
            </div>
            <p className="text-2xl font-bold">
              {metrics?.context_tokens?.toLocaleString() || 0}
            </p>
          </motion.div>
        </div>

        {/* Learning Progress */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Learning Progress</span>
            <span className="text-sm text-muted-foreground">
              {Math.round(animatedProgress)}%
            </span>
          </div>
          <Progress 
            value={animatedProgress} 
            className="h-2 transition-all duration-1000 ease-out"
          />
          <p className="text-xs text-muted-foreground">
            Continuous learning and self-improvement
          </p>
        </div>

        {/* Status Indicators */}
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className="text-xs">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
            WebSocket Connected
          </Badge>
          <Badge variant="outline" className="text-xs">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-1"></span>
            Context7 Active
          </Badge>
          <Badge variant="outline" className="text-xs">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-1"></span>
            Claudia Integrated
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}