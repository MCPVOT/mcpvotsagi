# MCPVotsAGI V3 Architecture Diagrams

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "F:\ Drive Storage Layer [853 GB]"
        subgraph "Data Infrastructure"
            RLD[RL Training Data<br/>200 GB]
            MKD[Market Data<br/>150 GB]
            MDL[Model Storage<br/>100 GB]
            MEM[Memory Store<br/>100 GB]
            TRD[Trading Logs<br/>50 GB]
            SEC[Security Data<br/>50 GB]
            IPFS[IPFS Storage<br/>100 GB]
            BKP[Backups<br/>50 GB]
            TEMP[Workspace<br/>53 GB]
        end
    end
    
    subgraph "Core Services Layer"
        subgraph "Critical Services"
            DS[DeepSeek MCP<br/>:3008]
            DT[DeepSeek Trading<br/>:3009]
            MM[Memory MCP<br/>:3002]
            SM[Solana MCP<br/>:3005]
        end
        
        subgraph "Support Services"
            OC[OpenCTI MCP<br/>:3007]
            GH[GitHub MCP<br/>:3001]
            BT[Browser MCP<br/>:3006]
            OLL[Ollama Service<br/>:11434]
        end
    end
    
    subgraph "Real-Time Processing"
        RTD[Dashboard<br/>:3011]
        MDC[Market Collector]
        SMC[Metrics Collector]
        RLM[RL Monitor]
        WS[WebSocket Server]
    end
    
    subgraph "Trading System"
        RLE[RL Engine]
        RD[Regime Detector]
        RM[Risk Manager]
        EX[Trade Executor]
        PM[Portfolio Manager]
    end
    
    subgraph "External APIs"
        YF[Yahoo Finance]
        AV[Alpha Vantage]
        CC[CryptoCompare]
        CB[Coinbase]
        JUP[Jupiter DEX]
    end
    
    %% Storage connections
    RLD --> RLE
    MKD --> MDC
    MDL --> DS
    MEM --> MM
    TRD --> PM
    SEC --> OC
    
    %% Service connections
    DS --> DT
    DT --> RLE
    MM --> DS
    SM --> EX
    
    %% Real-time flow
    MDC --> MKD
    SMC --> RTD
    RLM --> RTD
    RTD --> WS
    
    %% Trading flow
    RLE --> RD
    RD --> RM
    RM --> EX
    EX --> SM
    EX --> TRD
    
    %% External data
    YF --> MDC
    AV --> MDC
    CC --> MDC
    JUP --> SM
    
    style DS fill:#ff9,stroke:#333,stroke-width:4px
    style DT fill:#9ff,stroke:#333,stroke-width:4px
    style RLD fill:#f96,stroke:#333,stroke-width:2px
    style RTD fill:#9f9,stroke:#333,stroke-width:4px
```

## 2. DeepSeek Integration Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant DeepSeek
    participant Storage
    participant Trading
    participant Blockchain
    
    User->>Dashboard: Access UI (localhost:3011)
    Dashboard->>DeepSeek: Request Analysis
    
    alt Market Analysis
        DeepSeek->>Storage: Load Historical Data
        Storage-->>DeepSeek: 5 Years OHLCV
        DeepSeek->>DeepSeek: Reasoning Process
        Note over DeepSeek: Temperature: 0.3<br/>Context: 8192 tokens
        DeepSeek-->>Dashboard: Trading Signal
    end
    
    alt Execute Trade
        Dashboard->>Trading: Execute Strategy
        Trading->>Trading: Check Risk Limits
        Trading->>Blockchain: Place Order
        Blockchain-->>Trading: Confirmation
        Trading->>Storage: Log Trade
        Trading-->>Dashboard: Update Status
    end
    
    loop Every 30 seconds
        Dashboard->>User: WebSocket Update
    end
```

## 3. RL/ML Training Pipeline

```mermaid
graph LR
    subgraph "Data Collection"
        MD[Market Data]
        TA[Technical Analysis]
        SA[Sentiment Analysis]
        OB[Order Books]
    end
    
    subgraph "Feature Engineering"
        FE[Feature Extraction]
        NM[Normalization]
        FS[Feature Selection]
    end
    
    subgraph "RL Training"
        ST[State Space<br/>50 features]
        DQN[Deep Q-Network<br/>[512, 256, 128]]
        ATT[Attention Layer<br/>4 heads]
        ACT[Action Space<br/>5 actions]
    end
    
    subgraph "Experience Replay"
        BUF[Buffer<br/>50M experiences]
        SAM[Sampling<br/>Batch: 256]
        PRI[Priority Replay]
    end
    
    subgraph "Execution"
        POL[Policy]
        EPS[ε-greedy<br/>ε: 1.0→0.01]
        TRD[Trade Execution]
    end
    
    MD --> FE
    TA --> FE
    SA --> FE
    OB --> FE
    
    FE --> NM
    NM --> FS
    FS --> ST
    
    ST --> DQN
    DQN --> ATT
    ATT --> ACT
    
    ACT --> BUF
    BUF --> SAM
    SAM --> DQN
    
    ACT --> POL
    POL --> EPS
    EPS --> TRD
    
    TRD --> BUF
```

## 4. Real-Time Data Flow

```mermaid
graph TB
    subgraph "Data Sources"
        YF[Yahoo Finance API]
        AV[Alpha Vantage API]
        CC[CryptoCompare API]
        CB[Coinbase API]
    end
    
    subgraph "Collection Layer"
        MDC[Market Data Collector]
        SMC[System Metrics Collector]
        RLM[RL Training Monitor]
    end
    
    subgraph "Processing"
        VAL[Validation]
        AGG[Aggregation]
        CACHE[Cache Layer]
    end
    
    subgraph "Storage"
        RT[Real-time DB<br/>SQLite]
        TS[Time Series<br/>Parquet]
        HDF[HDF5 Arrays]
    end
    
    subgraph "Distribution"
        WS[WebSocket Server]
        API[REST API]
        DASH[Dashboard UI]
    end
    
    YF --> MDC
    AV --> MDC
    CC --> MDC
    CB --> MDC
    
    MDC --> VAL
    SMC --> VAL
    RLM --> VAL
    
    VAL --> AGG
    AGG --> CACHE
    
    CACHE --> RT
    CACHE --> TS
    CACHE --> HDF
    
    RT --> WS
    RT --> API
    
    WS --> DASH
    API --> DASH
    
    style WS fill:#9ff,stroke:#333,stroke-width:2px
    style CACHE fill:#ff9,stroke:#333,stroke-width:2px
```

## 5. Self-Healing Architecture

```mermaid
stateDiagram-v2
    [*] --> Healthy
    
    Healthy --> Monitoring: Continuous
    Monitoring --> Healthy: All OK
    
    Monitoring --> Unhealthy: Failure Detected
    Unhealthy --> Analyzing: Diagnose Issue
    
    Analyzing --> SelfHeal: Known Issue
    Analyzing --> Alert: Unknown Issue
    
    SelfHeal --> Restarting: Attempt Recovery
    Restarting --> Healthy: Success
    Restarting --> Failed: Max Retries
    
    Failed --> Alert: Notify Admin
    Alert --> Manual: Human Intervention
    Manual --> Healthy: Fixed
    
    state SelfHeal {
        [*] --> CheckDeps
        CheckDeps --> RestartService
        RestartService --> ValidateHealth
        ValidateHealth --> [*]
    }
    
    state Monitoring {
        [*] --> HealthCheck
        HealthCheck --> ResourceCheck
        ResourceCheck --> DependencyCheck
        DependencyCheck --> [*]
    }
```

## 6. Trading Decision Flow

```mermaid
flowchart TD
    Start([Market Tick]) --> A[Collect Data]
    
    A --> B{Data Valid?}
    B -->|No| End([Skip])
    B -->|Yes| C[Feature Extraction]
    
    C --> D[DeepSeek Analysis]
    C --> E[RL Prediction]
    C --> F[Technical Indicators]
    
    D --> G[Ensemble Score]
    E --> G
    F --> G
    
    G --> H{Confidence > 70%?}
    H -->|No| End
    H -->|Yes| I[Risk Assessment]
    
    I --> J{Risk OK?}
    J -->|No| End
    J -->|Yes| K[Position Sizing]
    
    K --> L[Order Preparation]
    L --> M[Execute Trade]
    
    M --> N[Log to F:\ Drive]
    N --> O[Update Portfolio]
    O --> P[Broadcast Update]
    
    P --> End
    
    style D fill:#ff9,stroke:#333,stroke-width:2px
    style M fill:#9f9,stroke:#333,stroke-width:2px
    style I fill:#f99,stroke:#333,stroke-width:2px
```

## 7. WebSocket Communication

```mermaid
graph LR
    subgraph "Clients"
        C1[Browser 1]
        C2[Browser 2]
        C3[API Client]
        C4[Mobile App]
    end
    
    subgraph "WebSocket Server"
        WS[WS Handler<br/>:3011/ws]
        SUB[Subscription<br/>Manager]
        BROAD[Broadcast<br/>Engine]
    end
    
    subgraph "Data Streams"
        PS[Price Stream]
        MS[Metrics Stream]
        TS[Trade Stream]
        RS[RL Stream]
    end
    
    C1 -->|Connect| WS
    C2 -->|Connect| WS
    C3 -->|Connect| WS
    C4 -->|Connect| WS
    
    WS --> SUB
    
    PS --> BROAD
    MS --> BROAD
    TS --> BROAD
    RS --> BROAD
    
    BROAD --> WS
    
    WS -->|Push| C1
    WS -->|Push| C2
    WS -->|Push| C3
    WS -->|Push| C4
    
    style WS fill:#9ff,stroke:#333,stroke-width:3px
    style BROAD fill:#ff9,stroke:#333,stroke-width:2px
```

## 8. Security Integration

```mermaid
graph TB
    subgraph "Threat Sources"
        GH[GitHub Commits]
        API[API Requests]
        NET[Network Traffic]
        SYS[System Events]
    end
    
    subgraph "OpenCTI Integration"
        IOC[IOC Database]
        STIX[STIX Parser]
        ATT[MITRE ATT&CK]
        TH[Threat Intel]
    end
    
    subgraph "Analysis Engine"
        ML[ML Detection]
        RULE[Rule Engine]
        COR[Correlation]
    end
    
    subgraph "Response"
        ALERT[Alerts]
        BLOCK[Blocking]
        ISO[Isolation]
        LOG[Logging]
    end
    
    subgraph "Storage"
        SIEM[SIEM Database]
        FOR[Forensics]
        REP[Reports]
    end
    
    GH --> IOC
    API --> IOC
    NET --> IOC
    SYS --> IOC
    
    IOC --> STIX
    STIX --> ATT
    ATT --> TH
    
    TH --> ML
    TH --> RULE
    ML --> COR
    RULE --> COR
    
    COR --> ALERT
    COR --> BLOCK
    COR --> ISO
    COR --> LOG
    
    LOG --> SIEM
    LOG --> FOR
    SIEM --> REP
    
    style IOC fill:#f99,stroke:#333,stroke-width:3px
    style COR fill:#ff9,stroke:#333,stroke-width:2px
```

## 9. Performance Monitoring

```mermaid
graph TB
    subgraph "Metrics Collection"
        CPU[CPU Usage]
        MEM[Memory Usage]
        DISK[Disk I/O]
        NET[Network I/O]
        GPU[GPU Usage]
    end
    
    subgraph "Service Metrics"
        LAT[Latency]
        THR[Throughput]
        ERR[Error Rate]
        AVL[Availability]
    end
    
    subgraph "Business Metrics"
        TPD[Trades/Day]
        PNL[P&L]
        SR[Sharpe Ratio]
        DD[Drawdown]
    end
    
    subgraph "Storage & Analysis"
        TS[(Time Series DB)]
        AGG[Aggregation]
        ALERT[Alert Engine]
        VIS[Visualization]
    end
    
    CPU --> TS
    MEM --> TS
    DISK --> TS
    NET --> TS
    GPU --> TS
    
    LAT --> TS
    THR --> TS
    ERR --> TS
    AVL --> TS
    
    TPD --> TS
    PNL --> TS
    SR --> TS
    DD --> TS
    
    TS --> AGG
    AGG --> ALERT
    AGG --> VIS
    
    ALERT -->|Webhook| Slack
    ALERT -->|Email| Admin
    VIS -->|Dashboard| UI
    
    style TS fill:#9ff,stroke:#333,stroke-width:3px
    style VIS fill:#9f9,stroke:#333,stroke-width:2px
```

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        DEV[Dev Environment]
        TEST[Testing]
        CI[CI/CD Pipeline]
    end
    
    subgraph "Production Server"
        subgraph "System Resources"
            CPU[16 Cores]
            RAM[32 GB RAM]
            GPU[NVIDIA GPU]
            SSD[F:\ 853 GB]
        end
        
        subgraph "Container Layer"
            DOCKER[Docker Engine]
            K8S[Kubernetes]
            HELM[Helm Charts]
        end
        
        subgraph "Services"
            CORE[Core Services]
            TRADE[Trading Engine]
            DATA[Data Collectors]
            MON[Monitoring]
        end
    end
    
    subgraph "Backup & Recovery"
        DAILY[Daily Backups]
        SNAP[Snapshots]
        REP[Replication]
    end
    
    DEV --> TEST
    TEST --> CI
    CI --> DOCKER
    
    DOCKER --> CORE
    DOCKER --> TRADE
    DOCKER --> DATA
    DOCKER --> MON
    
    CORE --> SSD
    TRADE --> SSD
    DATA --> SSD
    
    SSD --> DAILY
    SSD --> SNAP
    SNAP --> REP
    
    style SSD fill:#ff9,stroke:#333,stroke-width:4px
    style DOCKER fill:#9ff,stroke:#333,stroke-width:3px
```

---

These diagrams provide a comprehensive view of the MCPVotsAGI V3 architecture, showing:

1. **Complete System Architecture**: Overall system layout with F:\ drive integration
2. **DeepSeek Integration Flow**: How reasoning integrates with trading
3. **RL/ML Training Pipeline**: The complete machine learning workflow
4. **Real-Time Data Flow**: From APIs to dashboard
5. **Self-Healing Architecture**: Automatic recovery mechanisms
6. **Trading Decision Flow**: Step-by-step trading logic
7. **WebSocket Communication**: Real-time update distribution
8. **Security Integration**: Threat detection and response
9. **Performance Monitoring**: Comprehensive metrics tracking
10. **Deployment Architecture**: Production deployment strategy

Each diagram uses consistent styling:
- 🟨 Yellow: Critical components
- 🟦 Blue: Communication/networking
- 🟩 Green: Success/execution
- 🟥 Red: Storage/critical data