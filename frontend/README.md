# 🎨 ULTIMATE AGI V3 - Modern Frontend Integration

This directory contains the modern React-based frontend for ULTIMATE AGI SYSTEM V3, featuring professional UI components, smooth animations, and real-time updates.

## 📂 Structure

```
frontend/
├── animate-ui/              # Animation component library
├── agi-dashboard/          # Main Next.js dashboard application
│   ├── src/
│   │   ├── app/           # Next.js app routes
│   │   ├── components/    # UI components
│   │   │   ├── agents/    # Agent management UI
│   │   │   ├── storage/   # System monitoring
│   │   │   ├── chat/      # Chat interface
│   │   │   └── models/    # Model orchestration
│   │   └── lib/
│   │       └── api/       # Backend API client
│   └── public/            # Static assets
└── nginx/                 # Reverse proxy configuration
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   cd agi-dashboard
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your backend URL
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Access Dashboard**
   Open http://localhost:3000

## 🔌 Backend Integration

The frontend connects to the Python backend via REST API and WebSocket:

- **REST API**: http://localhost:8889/api/*
- **WebSocket**: ws://localhost:8889/ws/v3/realtime

## 🎯 Key Features

- ✅ Real-time agent status monitoring
- ✅ Real-time system monitoring
- ✅ Animated chat interface
- ✅ Model orchestration dashboard
- ✅ Command palette (Cmd+K)
- ✅ Dark mode support
- ✅ Mobile responsive

## 📚 Documentation

- [API Integration Guide](./docs/API_INTEGRATION.md)
- [Component Library](./docs/COMPONENTS.md)
- [Animation Guide](./docs/ANIMATIONS.md)