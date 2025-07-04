# Oracle AGI Ultimate Architecture

## System Overview

```mermaid
graph TB
    subgraph "Ultimate Unified Dashboard (Port 3010)"
        UD[Ultimate Dashboard<br/>ONE Interface]
        WS[WebSocket Layer]
        RT[Real-Time Handler]
    end
    
    subgraph "UI Frameworks"
        AGUI[AG-UI Protocol]
        LOBE[Lobe Chat]
        IIAGENT[II-Agent]
        MAG[Magnitude]
        ANIM[Animate-UI]
        CTM[Continuous Thought]
    end
    
    subgraph "Oracle AGI Core Services"
        ORACLE[Oracle AGI Core<br/>Port 8888]
        TRILOGY[Trilogy Brain<br/>Port 8887]
        DGM[DGM Voltagents<br/>Port 8886]
    end
    
    subgraph "Real Integration Layer"
        RIC[Real Integration<br/>Connector]
        DEFI[DeFi Monitor]
        GAS[Gas Tracker]
        ARB[Arbitrage Scanner]
    end
    
    subgraph "External Services"
        UNI[Uniswap API]
        AAVE[Aave API]
        COMP[Compound API]
        CURVE[Curve API]
        ETHERSCAN[Etherscan]
        BLOCKNATIVE[Blocknative]
    end
    
    subgraph "Claudia Integration"
        CLAUDIA[Claudia<br/>Port 3003]
        CAGENTS[Oracle Agents<br/>for Claudia]
    end
    
    %% Connections
    UD --> WS
    WS --> RT
    RT --> RIC
    
    UD --> AGUI
    UD --> LOBE
    UD --> IIAGENT
    UD --> MAG
    UD --> ANIM
    UD --> CTM
    
    RIC --> ORACLE
    RIC --> TRILOGY
    RIC --> DGM
    
    RIC --> DEFI
    RIC --> GAS
    RIC --> ARB
    
    DEFI --> UNI
    DEFI --> AAVE
    DEFI --> COMP
    DEFI --> CURVE
    
    GAS --> ETHERSCAN
    GAS --> BLOCKNATIVE
    
    ORACLE <--> CLAUDIA
    CLAUDIA --> CAGENTS
    
    %% Styling
    classDef ultimate fill:#00ffff,stroke:#00ff88,stroke-width:4px
    classDef framework fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    classDef service fill:#00ff88,stroke:#fff,stroke-width:2px
    classDef external fill:#ffaa00,stroke:#fff,stroke-width:2px
    classDef real fill:#ff6b6b,stroke:#fff,stroke-width:3px
    
    class UD ultimate
    class AGUI,LOBE,IIAGENT,MAG,ANIM,CTM framework
    class ORACLE,TRILOGY,DGM service
    class UNI,AAVE,COMP,CURVE,ETHERSCAN,BLOCKNATIVE external
    class RIC,DEFI,GAS,ARB real
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant WebSocket
    participant RealConnector
    participant OracleCore
    participant DeFiAPIs
    participant Claudia
    
    User->>Dashboard: Access http://localhost:3010
    Dashboard->>WebSocket: Connect
    WebSocket->>RealConnector: Initialize monitors
    
    loop Real-Time Monitoring
        RealConnector->>DeFiAPIs: Fetch protocol data
        DeFiAPIs-->>RealConnector: Return data
        RealConnector->>WebSocket: Send updates
        WebSocket->>Dashboard: Display real data
    end
    
    User->>Dashboard: Send chat message
    Dashboard->>RealConnector: Process with Oracle
    RealConnector->>OracleCore: Analyze query
    OracleCore-->>RealConnector: Return analysis
    RealConnector-->>Dashboard: Display response
    
    Note over Claudia: Project Management
    Claudia->>OracleCore: Request agent action
    OracleCore->>Claudia: Execute & respond
```

## Component Details

### Ultimate Unified Dashboard
- **Port**: 3010
- **Purpose**: Single interface for all functionality
- **Features**: Real-time updates, no mock data

### Real Integration Connector
```python
class OracleAGIRealConnector:
    - get_oracle_analysis()      # Real Oracle AGI
    - get_trilogy_prediction()   # Real Trilogy Brain
    - get_dgm_trading_status()   # Real DGM status
    - monitor_defi_protocols()   # Real DeFi data
    - get_gas_prices()          # Real gas prices
    - detect_arbitrage()        # Real opportunities
```

### Real-Time Monitoring
- **DeFi Protocols**: Every 30 seconds
- **Gas Prices**: Every 15 seconds  
- **Arbitrage**: Every 10 seconds

### Claudia Integration

Oracle agents available to Claudia:

```yaml
oracle-planner:
  name: "Oracle Strategic Planner"
  capabilities:
    - task_decomposition
    - strategy_planning
    - consensus_building

oracle-executor:
  name: "Oracle Task Executor"
  capabilities:
    - task_execution
    - progress_monitoring
    - error_handling

oracle-reflector:
  name: "Oracle Performance Analyzer"
  capabilities:
    - performance_analysis
    - optimization_suggestions
    - learning_integration

oracle-knowledge:
  name: "Oracle Knowledge Manager"
  capabilities:
    - memory_management
    - context_retrieval
    - knowledge_synthesis
```

## No Mocks Policy

Every component uses REAL data:

✅ **Real DeFi Data**
- Direct API calls to Uniswap, Aave, Compound, Curve
- No simulated liquidity or TVL

✅ **Real Gas Prices**
- Live data from Etherscan and Blocknative
- No hardcoded values

✅ **Real Arbitrage**
- Actual price comparisons across exchanges
- No fake opportunities

✅ **Real Browser Automation**
- Actual web scraping with Magnitude/Playwright
- No simulated browser actions

✅ **Real Oracle Analysis**
- Connected to live Oracle AGI services
- No mock responses

## WebSocket Events

Real events sent to dashboard:

```javascript
// DeFi Protocol Update
{
  type: 'magnitude_log',
  message: 'Monitoring 4 DeFi protocols (2 online)',
  data: { 
    protocols: {
      uniswap: { status: 'online', tvl: 5234567890 },
      aave: { status: 'online', tvl: 3456789012 }
    }
  }
}

// Gas Price Update
{
  type: 'magnitude_log',
  message: 'Updated gas prices from 2 sources',
  data: {
    gas_prices: {
      etherscan: { fast: 45, average: 35, slow: 25 },
      blocknative: { fast: 47, average: 36, slow: 26 }
    }
  }
}

// Arbitrage Opportunity
{
  type: 'magnitude_log',
  message: 'Detected 1 arbitrage opportunity!',
  data: {
    opportunities: [{
      pair: 'ETH/USDT',
      buyExchange: 'binance',
      sellExchange: 'coinbase',
      profitPercent: 0.34
    }]
  }
}
```

## Deployment

1. **Development**: Run directly with Python
2. **Production**: Use START_PRODUCTION.bat
3. **Docker**: Coming soon

## Monitoring

Check system health:
```bash
python check_production_status.py
```

View logs in real-time through the dashboard WebSocket connection.