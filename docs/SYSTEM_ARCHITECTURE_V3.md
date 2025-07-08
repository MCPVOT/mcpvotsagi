# 🏗️ MCPVotsAGI System Architecture v3.0
**Enhanced with DeepSeek-R1 and Jupiter DEX Integration**

## 📊 System Overview

```mermaid
graph TB
    subgraph "AI Tool Stack"
        A[Claudia Enhanced<br/>Opus 4 + Sonnet 4 + DeepSeek-R1]
        B[Claude Code WSL<br/>Code Optimization]
        C[Copilot Opus 4<br/>GitHub Research]
        D[GitHub Copilot<br/>Local Coordination]
    end

    subgraph "Core Systems"
        E[Ultimate AGI System V3<br/>Port 8889]
        F[MCPVotsAGI Frontend<br/>Port 3002]
        G[RL Training Monitor<br/>Port 8891]
        H[Knowledge Graph Browser<br/>Integrated]
    end

    subgraph "Jupiter DEX Integration"
        I[Jupiter Terminal<br/>Cloned]
        J[Jupiter API Wrapper<br/>Python]
        K[Jupiter RL Integration<br/>Trading Strategies]
        L[Jupiter Perpetual Trading<br/>Advanced Algorithms]
    end

    subgraph "Storage Systems"
        M[F: Drive Storage<br/>200GB RL Trading]
        N[MCP Memory<br/>Knowledge Graph]
        O[Dashboard Metrics DB<br/>SQLite]
    end

    subgraph "Model Routing"
        P[Claude Opus 4<br/>Complex Reasoning]
        Q[Claude Sonnet 4<br/>Code Generation]
        R[DeepSeek-R1<br/>Mathematical Analysis]
        S[Claude Haiku<br/>Quick Tasks]
    end

    A --> E
    A --> P
    A --> Q
    A --> R
    A --> S
    B --> A
    C --> A
    D --> E
    E --> F
    E --> G
    E --> H
    E --> J
    J --> I
    J --> K
    K --> L
    K --> G
    G --> M
    H --> N
    E --> O

    style A fill:#ff9999
    style E fill:#99ccff
    style J fill:#99ff99
    style R fill:#ffcc99
```

## 🧠 Model Selection Strategy

```mermaid
flowchart TD
    A[Task Input] --> B{Task Type Analysis}

    B -->|Mathematical Reasoning<br/>Trading Analysis<br/>Risk Calculation| C[DeepSeek-R1<br/>Q4_K_XL 5.1GB]
    B -->|Complex Strategy<br/>System Design<br/>Architecture| D[Claude Opus 4<br/>Advanced Reasoning]
    B -->|Code Generation<br/>TypeScript/React<br/>API Integration| E[Claude Sonnet 4<br/>Balanced Performance]
    B -->|Quick Response<br/>Simple Queries<br/>Status Checks| F[Claude Haiku<br/>Fast Execution]

    C --> G[Mathematical Output]
    D --> H[Strategic Analysis]
    E --> I[Code Generation]
    F --> J[Quick Response]

    G --> K[Jupiter Trading Algorithms]
    H --> L[System Architecture]
    I --> M[React Components]
    J --> N[Status Updates]

    style C fill:#ffcc99
    style D fill:#ff9999
    style E fill:#99ccff
    style F fill:#99ff99
```

## 🔄 Jupiter DEX Integration Flow

```mermaid
sequenceDiagram
    participant U as User Interface
    participant C as Claudia Enhanced
    participant DS as DeepSeek-R1
    participant JA as Jupiter API
    participant RL as RL Training
    participant FS as F: Drive Storage

    U->>C: Request Trading Analysis
    C->>DS: Mathematical Analysis Task
    DS->>DS: Calculate Risk Metrics
    DS->>C: Return Calculations
    C->>JA: Get Market Data
    JA->>JA: Fetch Jupiter Quotes
    JA->>C: Return Market Data
    C->>RL: Send Combined Analysis
    RL->>RL: Train Strategy
    RL->>FS: Store Results
    FS->>C: Confirm Storage
    C->>U: Return Trading Recommendation
```

## 🏢 Component Architecture

```mermaid
graph LR
    subgraph "Frontend Layer"
        A[React Frontend<br/>Port 3002]
        B[Knowledge Graph Browser<br/>Integrated]
        C[Jupiter Terminal UI<br/>Cloned]
    end

    subgraph "API Layer"
        D[Ultimate AGI System V3<br/>Port 8889]
        E[Jupiter API Wrapper<br/>Python]
        F[RL Training API<br/>Port 8891]
    end

    subgraph "Processing Layer"
        G[Claudia Enhanced<br/>Multi-Model]
        H[DeepSeek-R1<br/>Mathematics]
        I[RL Training Monitor<br/>Algorithms]
    end

    subgraph "Storage Layer"
        J[F: Drive<br/>RL Trading Data]
        K[MCP Memory<br/>Knowledge Graph]
        L[SQLite DB<br/>Metrics]
    end

    A --> D
    B --> D
    C --> E
    D --> G
    E --> H
    F --> I
    G --> K
    H --> J
    I --> L
```

## 📊 Model Performance Matrix

| Model | Use Case | Tokens | Temperature | Performance |
|-------|----------|--------|-------------|-------------|
| **DeepSeek-R1** | Mathematical Trading Analysis | 8192 | 0.15 | ⭐⭐⭐⭐⭐ |
| **Claude Opus 4** | Complex Strategy Planning | 4096 | 0.1 | ⭐⭐⭐⭐⭐ |
| **Claude Sonnet 4** | Code Generation | 4096 | 0.2 | ⭐⭐⭐⭐ |
| **Claude Haiku** | Quick Responses | 2048 | 0.3 | ⭐⭐⭐ |

## 🔧 Deployment Architecture

```mermaid
graph TB
    subgraph "Windows Environment"
        A[VS Code<br/>GitHub Copilot]
        B[PowerShell<br/>Scripts]
        C[Python 3.12<br/>Environment]
    end

    subgraph "WSL Environment"
        D[Claude Code<br/>Optimization]
        E[Node.js<br/>Claudia GUI]
        F[Bun Runtime<br/>Modern JS]
    end

    subgraph "Web Environment"
        G[VS Code Web<br/>Copilot Opus 4]
        H[GitHub Access<br/>Full Repository]
        I[Documentation<br/>Research]
    end

    subgraph "Local Services"
        J[Port 8889<br/>Ultimate AGI]
        K[Port 3002<br/>Frontend]
        L[Port 8891<br/>RL Monitor]
        M[Port 3333<br/>Claudia GUI]
    end

    A --> C
    B --> C
    C --> J
    D --> E
    E --> M
    F --> E
    G --> H
    H --> I
    J --> K
    K --> L
    M --> J
```

## 🚀 Performance Optimization

```mermaid
flowchart LR
    A[Request] --> B{Model Router}
    B -->|Math/Trading| C[DeepSeek-R1<br/>5.1GB RAM]
    B -->|Complex| D[Opus 4<br/>Cloud API]
    B -->|Code| E[Sonnet 4<br/>Cloud API]
    B -->|Quick| F[Haiku<br/>Cloud API]

    C --> G[Local Processing<br/>Fast Response]
    D --> H[Cloud Processing<br/>Advanced Reasoning]
    E --> I[Cloud Processing<br/>Code Quality]
    F --> J[Cloud Processing<br/>Quick Response]

    G --> K[Cache Results]
    H --> K
    I --> K
    J --> K

    K --> L[Response to User]

    style C fill:#ffcc99
    style G fill:#99ff99
    style K fill:#cccccc
```

## 📁 Directory Structure

```
MCPVotsAGI/
├── 🧠 AI Models & Agents
│   ├── claudia/                    # Claudia Enhanced GUI
│   │   ├── src/config/models.json  # Model configurations
│   │   ├── cc_agents/              # Enhanced agent templates
│   │   └── start_enhanced.py       # Startup script
│   ├── Claude-Code-Usage-Monitor/  # Usage monitoring
│   └── deepseek_trading_agent.py   # DeepSeek integration
│
├── 🚀 Jupiter DEX Integration
│   ├── jupiter-terminal/           # Cloned Jupiter UI
│   ├── jupiter-swap-api-client/    # API client
│   ├── jupiter-cpi-swap-example/   # CPI examples
│   ├── jupiter_api_wrapper.py      # Python wrapper
│   └── jupiter_rl_integration.py   # RL integration
│
├── 🏗️ Core Systems
│   ├── src/core/                   # Core AGI system
│   │   ├── ULTIMATE_AGI_SYSTEM_V3.py
│   │   └── claudia_integration_bridge.py
│   ├── frontend/                   # React frontend
│   └── real_rl_training_monitor.py # RL training
│
├── 💾 Storage & Data
│   ├── F:/ULTIMATE_AGI_DATA/       # F: drive storage
│   │   ├── RL_TRADING/             # Trading data
│   │   ├── CHAT_MEMORY/            # Conversations
│   │   └── KNOWLEDGE_GRAPH/        # Graph data
│   └── ecosystem_knowledge.db      # Local database
│
└── 📚 Documentation
    ├── COMPLETE_AI_TOOL_STACK_FINAL.md
    ├── JUPITER_DEX_INTEGRATION_REPORT.md
    └── SYSTEM_ARCHITECTURE_V3.md      # This file
```

## 🔄 Integration Workflow

```mermaid
stateDiagram-v2
    [*] --> Initialized
    Initialized --> ModelsLoaded: Load AI Models
    ModelsLoaded --> JupiterIntegrated: Setup Jupiter DEX
    JupiterIntegrated --> RLTraining: Initialize RL System
    RLTraining --> ProductionReady: Validate All Systems

    ProductionReady --> TradingAnalysis: User Request
    TradingAnalysis --> ModelSelection: Route to Best Model
    ModelSelection --> DeepSeekR1: Mathematical Task
    ModelSelection --> OpusClaud: Complex Strategy
    ModelSelection --> SonnetClaud: Code Generation

    DeepSeekR1 --> ResultProcessing: Return Analysis
    OpusClaud --> ResultProcessing: Return Strategy
    SonnetClaud --> ResultProcessing: Return Code

    ResultProcessing --> StorageUpdate: Save Results
    StorageUpdate --> UserResponse: Send Response
    UserResponse --> ProductionReady: Ready for Next

    ProductionReady --> [*]: System Shutdown
```

## 🎯 Success Metrics

### Technical Performance
- **Model Response Time**: < 2 seconds for DeepSeek-R1 local processing
- **API Throughput**: > 100 requests/minute across all models
- **Memory Usage**: < 8GB total system usage
- **Storage Efficiency**: Compressed data storage in F: drive

### Integration Quality
- **Model Accuracy**: > 95% appropriate model selection
- **System Uptime**: > 99.5% availability
- **Error Rate**: < 1% failed requests
- **User Satisfaction**: Seamless multi-model experience

### Jupiter DEX Performance
- **Trading Latency**: < 500ms for quote requests
- **RL Training Speed**: Real-time strategy updates
- **Risk Management**: 100% automated risk checks
- **Profit Optimization**: Continuous strategy improvement

---

**System Architecture v3.0 - Enhanced with DeepSeek-R1 Mathematical Reasoning**
*Last Updated: July 6, 2025*
