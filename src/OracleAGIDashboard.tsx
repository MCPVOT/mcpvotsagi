import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  IconButton,
  Paper,
  Tabs,
  Tab,
  Alert,
  Snackbar,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp,
  Chat,
  Memory,
  GitHub,
  Storage,
  Speed,
  Security,
  Refresh,
  PlayArrow,
  Stop,
  CheckCircle,
  Error,
  Warning,
  Info,
  AttachMoney,
  Psychology,
  Timeline,
  Code,
  CloudSync
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Styled components for cyberpunk theme
const CyberCard = styled(Card)(({ theme }) => ({
  background: 'rgba(0, 0, 0, 0.8)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(0, 255, 136, 0.3)',
  borderRadius: '15px',
  transition: 'all 0.3s ease',
  '&:hover': {
    border: '1px solid rgba(0, 255, 136, 0.6)',
    transform: 'translateY(-2px)',
    boxShadow: '0 10px 30px rgba(0, 255, 136, 0.3)'
  }
}));

const GlowingButton = styled(Button)(({ theme }) => ({
  background: 'linear-gradient(45deg, #00ff88 30%, #00d4ff 90%)',
  border: 0,
  borderRadius: 25,
  boxShadow: '0 3px 15px 2px rgba(0, 255, 136, .3)',
  color: 'black',
  fontWeight: 'bold',
  padding: '10px 30px',
  '&:hover': {
    boxShadow: '0 5px 20px 2px rgba(0, 255, 136, .5)',
  },
}));

const StatusBadge = styled(Badge)(({ status }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: status === 'online' ? '#00ff88' : 
                    status === 'warning' ? '#ffaa00' : '#ff4444',
    color: status === 'online' ? '#00ff88' : 
           status === 'warning' ? '#ffaa00' : '#ff4444',
    boxShadow: `0 0 0 2px rgba(0, 0, 0, 0.8)`,
    '&::after': {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      borderRadius: '50%',
      animation: status === 'online' ? 'ripple 1.2s infinite ease-in-out' : 'none',
      border: '1px solid currentColor',
      content: '""',
    },
  },
  '@keyframes ripple': {
    '0%': {
      transform: 'scale(.8)',
      opacity: 1,
    },
    '100%': {
      transform: 'scale(2.4)',
      opacity: 0,
    },
  },
}));

// Service Status Interface
interface ServiceStatus {
  name: string;
  status: 'online' | 'offline' | 'warning';
  port: number;
  health: number;
  lastCheck: string;
}

// Trading Signal Interface
interface TradingSignal {
  id: string;
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  entry: number;
  stopLoss: number;
  takeProfit: number;
  aiConsensus: string;
  timestamp: string;
}

// Chat Message Interface
interface ChatMessage {
  id: string;
  user: string;
  ai: string;
  model: string;
  timestamp: string;
}

// Main Dashboard Component
export const OracleAGIDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [tradingSignals, setTradingSignals] = useState<TradingSignal[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [selectedModel, setSelectedModel] = useState('gemini');
  const [chatInput, setChatInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    fetchSystemStatus();
    fetchTradingSignals();
    
    const interval = setInterval(() => {
      fetchSystemStatus();
      fetchTradingSignals();
    }, 5000);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    wsRef.current = new WebSocket('ws://localhost:3002/ws');
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
      wsRef.current?.send(JSON.stringify({
        type: 'subscribe',
        channels: ['status', 'trading', 'chat', 'metrics']
      }));
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      showNotification('WebSocket connection error', 'error');
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      setTimeout(connectWebSocket, 5000);
    };
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'system_update':
        updateSystemStatus(data.data);
        break;
      case 'trading_signal':
        addTradingSignal(data.data);
        break;
      case 'chat_response':
        addChatMessage(data.data);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      
      const serviceList: ServiceStatus[] = Object.entries(data.services).map(([id, service]: any) => ({
        name: service.name,
        status: service.healthy ? 'online' : 'offline',
        port: service.port,
        health: service.healthy ? 100 : 0,
        lastCheck: new Date().toISOString()
      }));
      
      setServices(serviceList);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  const fetchTradingSignals = async () => {
    try {
      const response = await fetch('/api/trading/signals');
      const data = await response.json();
      setTradingSignals(data.signals || []);
    } catch (error) {
      console.error('Failed to fetch signals:', error);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: chatInput, model: selectedModel })
      });
      const data = await response.json();
      
      setChatMessages([...chatMessages, {
        id: Date.now().toString(),
        user: chatInput,
        ai: data.response,
        model: selectedModel,
        timestamp: new Date().toISOString()
      }]);
      
      setChatInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
      showNotification('Failed to send message', 'error');
    } finally {
      setLoading(false);
    }
  };

  const updateSystemStatus = (data: any) => {
    // Update system status from WebSocket
  };

  const addTradingSignal = (signal: TradingSignal) => {
    setTradingSignals(prev => [signal, ...prev].slice(0, 20));
    showNotification(`New ${signal.action} signal for ${signal.symbol}`, 'info');
  };

  const addChatMessage = (message: ChatMessage) => {
    setChatMessages(prev => [...prev, message]);
  };

  const showNotification = (message: string, severity: string) => {
    setNotification({ open: true, message, severity });
  };

  const getServiceIcon = (serviceName: string) => {
    if (serviceName.includes('Oracle')) return <Psychology />;
    if (serviceName.includes('Trading')) return <TrendingUp />;
    if (serviceName.includes('Chat')) return <Chat />;
    if (serviceName.includes('Memory')) return <Memory />;
    if (serviceName.includes('GitHub')) return <GitHub />;
    if (serviceName.includes('Telemetry')) return <Timeline />;
    if (serviceName.includes('Self-Healing')) return <Security />;
    return <DashboardIcon />;
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      backgroundColor: '#0a0a0a',
      backgroundImage: `
        linear-gradient(rgba(0, 255, 136, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 136, 0.05) 1px, transparent 1px)
      `,
      backgroundSize: '50px 50px',
      color: 'white',
      p: 3
    }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h2" sx={{
          background: 'linear-gradient(45deg, #00ff88 30%, #00d4ff 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 'bold',
          mb: 1
        }}>
          🔮 Oracle AGI V5
        </Typography>
        <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          Unified AI Trading Dashboard with MCP Integration
        </Typography>
      </Box>

      {/* Tabs */}
      <Paper sx={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={(e, v) => setTabValue(v)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="System Overview" icon={<DashboardIcon />} />
          <Tab label="Trading Signals" icon={<TrendingUp />} />
          <Tab label="AI Chat" icon={<Chat />} />
          <Tab label="MCP Tools" icon={<Code />} />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Service Status Grid */}
          {services.map((service, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <CyberCard>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box display="flex" alignItems="center">
                      <StatusBadge
                        overlap="circular"
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        variant="dot"
                        status={service.status}
                      >
                        <Avatar sx={{ bgcolor: 'rgba(0, 255, 136, 0.1)' }}>
                          {getServiceIcon(service.name)}
                        </Avatar>
                      </StatusBadge>
                      <Box ml={2}>
                        <Typography variant="h6" sx={{ fontSize: '1rem' }}>
                          {service.name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                          Port: {service.port}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={service.health} 
                    sx={{ 
                      mt: 2,
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        background: service.status === 'online' ? 
                          'linear-gradient(45deg, #00ff88 30%, #00d4ff 90%)' :
                          'linear-gradient(45deg, #ff4444 30%, #ff6666 90%)'
                      }
                    }}
                  />
                </CardContent>
              </CyberCard>
            </Grid>
          ))}

          {/* Performance Metrics */}
          <Grid item xs={12}>
            <CyberCard>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  📊 Performance Metrics
                </Typography>
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" sx={{ color: '#00ff88' }}>94.2%</Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                        Success Rate
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" sx={{ color: '#00d4ff' }}>0.87</Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                        Avg Confidence
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" sx={{ color: '#ffaa00' }}>147</Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                        Decisions/Day
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" sx={{ color: '#ff00ff' }}>5/5</Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                        Active Models
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </CyberCard>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <CyberCard>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <Typography variant="h5">📈 Trading Signals</Typography>
                  <GlowingButton startIcon={<Refresh />} onClick={fetchTradingSignals}>
                    Refresh
                  </GlowingButton>
                </Box>
                
                <List>
                  {tradingSignals.map((signal, index) => (
                    <ListItem 
                      key={signal.id || index}
                      sx={{ 
                        backgroundColor: 'rgba(0, 255, 136, 0.05)',
                        mb: 1,
                        borderRadius: 2,
                        border: '1px solid rgba(0, 255, 136, 0.2)'
                      }}
                    >
                      <ListItemIcon>
                        <Avatar sx={{
                          bgcolor: signal.action === 'BUY' ? 'success.main' :
                                  signal.action === 'SELL' ? 'error.main' : 'warning.main'
                        }}>
                          <AttachMoney />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" justifyContent="space-between">
                            <Typography variant="h6">{signal.symbol}</Typography>
                            <Chip 
                              label={signal.action} 
                              color={signal.action === 'BUY' ? 'success' :
                                    signal.action === 'SELL' ? 'error' : 'warning'}
                            />
                          </Box>
                        }
                        secondary={
                          <Grid container spacing={2} sx={{ mt: 1 }}>
                            <Grid item xs={3}>
                              <Typography variant="body2" color="text.secondary">
                                Confidence: {(signal.confidence * 100).toFixed(1)}%
                              </Typography>
                            </Grid>
                            <Grid item xs={3}>
                              <Typography variant="body2" color="text.secondary">
                                Entry: ${signal.entry}
                              </Typography>
                            </Grid>
                            <Grid item xs={3}>
                              <Typography variant="body2" color="text.secondary">
                                Stop Loss: ${signal.stopLoss}
                              </Typography>
                            </Grid>
                            <Grid item xs={3}>
                              <Typography variant="body2" color="text.secondary">
                                Take Profit: ${signal.takeProfit}
                              </Typography>
                            </Grid>
                          </Grid>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </CyberCard>
          </Grid>
        </Grid>
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <CyberCard sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h5">🤖 AI Assistant</Typography>
                  <Select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    size="small"
                    sx={{ minWidth: 150 }}
                  >
                    <MenuItem value="gemini">Gemini 2.5</MenuItem>
                    <MenuItem value="deepseek">DeepSeek R1</MenuItem>
                    <MenuItem value="claude">Claude 3.7</MenuItem>
                    <MenuItem value="gpt4">GPT-4 Turbo</MenuItem>
                  </Select>
                </Box>
                
                <Box sx={{ flex: 1, overflowY: 'auto', mb: 2 }}>
                  {chatMessages.map((msg, index) => (
                    <Box key={msg.id || index} mb={2}>
                      <Box sx={{ 
                        backgroundColor: 'rgba(0, 100, 255, 0.2)',
                        p: 2,
                        borderRadius: 2,
                        mb: 1
                      }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>You:</Typography>
                        <Typography>{msg.user}</Typography>
                      </Box>
                      <Box sx={{ 
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        p: 2,
                        borderRadius: 2
                      }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {msg.model}:
                        </Typography>
                        <Typography>{msg.ai}</Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
                
                <Box display="flex" gap={1}>
                  <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Ask anything..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !loading) {
                        sendChatMessage();
                      }
                    }}
                    disabled={loading}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        color: 'white',
                        '& fieldset': {
                          borderColor: 'rgba(0, 255, 136, 0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: 'rgba(0, 255, 136, 0.5)',
                        },
                      },
                    }}
                  />
                  <GlowingButton 
                    onClick={sendChatMessage} 
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                  >
                    Send
                  </GlowingButton>
                </Box>
              </CardContent>
            </CyberCard>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <CyberCard>
              <CardContent>
                <Typography variant="h6" gutterBottom>Model Capabilities</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon><CheckCircle sx={{ color: '#00ff88' }} /></ListItemIcon>
                    <ListItemText 
                      primary="Gemini 2.5" 
                      secondary="Reasoning, Code, Analysis"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircle sx={{ color: '#00ff88' }} /></ListItemIcon>
                    <ListItemText 
                      primary="DeepSeek R1" 
                      secondary="Trading, Patterns, Optimization"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircle sx={{ color: '#00ff88' }} /></ListItemIcon>
                    <ListItemText 
                      primary="Claude 3.7" 
                      secondary="Agents, Workflows, Integration"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircle sx={{ color: '#00ff88' }} /></ListItemIcon>
                    <ListItemText 
                      primary="GPT-4 Turbo" 
                      secondary="General, Creative, Planning"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </CyberCard>
          </Grid>
        </Grid>
      )}

      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <CyberCard>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  <Memory sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Memory Vault
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText 
                      primary="Knowledge Graph" 
                      secondary="12.4K memories stored"
                    />
                    <Chip label="Active" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Pattern Recognition" 
                      secondary="89 patterns identified"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Historical Backtesting" 
                      secondary="76% accuracy rate"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </CyberCard>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <CyberCard>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  <GitHub sx={{ mr: 1, verticalAlign: 'middle' }} />
                  GitHub Integration
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText 
                      primary="kabrony/MCPVots" 
                      secondary="Main orchestration repository"
                    />
                    <IconButton size="small">
                      <CloudSync />
                    </IconButton>
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="kabrony/voltagent" 
                      secondary="AI agent framework"
                    />
                    <IconButton size="small">
                      <CloudSync />
                    </IconButton>
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="kabrony/lobe-chat" 
                      secondary="Chat interface"
                    />
                    <IconButton size="small">
                      <CloudSync />
                    </IconButton>
                  </ListItem>
                </List>
              </CardContent>
            </CyberCard>
          </Grid>
        </Grid>
      )}

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert 
          onClose={() => setNotification({ ...notification, open: false })}
          severity={notification.severity as any}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};