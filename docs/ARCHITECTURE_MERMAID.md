# MCPVotsAGI Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        WEB[Web Dashboard<br/>Port 8900]
        WS[WebSocket<br/>Real-time Updates]
    end

    subgraph "AI Agent Layer"
        CLAUDIA[Claudia AI<br/>MCP Enhanced]
        DEEPSEEK[DeepSeek R1<br/>Reasoning Engine]
        ORCHESTRATOR[Agent Orchestrator<br/>Load Balancing]
    end

    subgraph "MCP Tools Layer"
        MEMORY[MCP Memory<br/>Knowledge Graph]
        GITHUB[MCP GitHub<br/>Code Management]
        FS[MCP FileSystem<br/>Workspace]
        BROWSER[MCP Browser<br/>Web Automation]
        SEARCH[MCP Search<br/>Information Retrieval]
    end

    subgraph "Backend Services"
        BACKEND[Ultimate AGI<br/>Port 8889]
        OLLAMA[Ollama Models<br/>Port 11434]
        DB[(SQLite Database)]
    end

    subgraph "Data Sources"
        JUPITER[Jupiter DEX API]
        NETWORK[Network Monitoring]
        SYSTEM[System Metrics]
    end

    WEB --> CLAUDIA
    WS --> CLAUDIA
    CLAUDIA --> MEMORY
    CLAUDIA --> GITHUB
    CLAUDIA --> FS
    CLAUDIA --> BROWSER
    CLAUDIA --> SEARCH
    CLAUDIA --> DEEPSEEK
    ORCHESTRATOR --> CLAUDIA
    CLAUDIA --> BACKEND
    BACKEND --> OLLAMA
    BACKEND --> DB
    CLAUDIA --> JUPITER
    CLAUDIA --> NETWORK
    CLAUDIA --> SYSTEM

    style CLAUDIA fill:#e1f5fe
    style MEMORY fill:#f3e5f5
    style WEB fill:#e8f5e8
    style BACKEND fill:#fff3e0
```

## System Flow

1. **User Interaction**: Web dashboard receives user requests
2. **AI Processing**: Claudia AI processes with MCP tool integration
3. **Context Retrieval**: MCP Memory provides historical context
4. **Multi-Tool Orchestration**: Uses GitHub, FileSystem, Browser, Search as needed
5. **Analysis Generation**: DeepSeek R1 generates insights
6. **Real-time Updates**: WebSocket streams results to dashboard

## Key Features

- **Async Architecture**: All operations are non-blocking
- **Circuit Breakers**: Fault tolerance and graceful degradation
- **Load Balancing**: Intelligent task distribution
- **Real-time Monitoring**: Prometheus metrics and health checks
- **Context Awareness**: Memory-driven decision making
