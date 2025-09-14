# FinanceGPT Pro - MCP Architecture Flow

## System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (React + TypeScript)"
        U[User] --> CI[Chat Interface]
        CI --> AIS[AI Chat Service]
    end

    subgraph "Backend (FastAPI + Python)"
        AIS --> CE[Chat Endpoint]
        CE --> ID[Intent Detection]
        ID --> TE[Tool Executor]
    end

    subgraph "MCP Tools Layer"
        TE --> MT[MCP Tools<br/>20+ Financial Tools]
        MT --> BA[Budget Analyzer]
        MT --> SC[Savings Calculator]
        MT --> IC[Investment Calculator]
        MT --> TC[Tax Calculator]
        MT --> MORE[...More Tools]
    end

    subgraph "AI Integration"
        CE --> GEM[Gemini AI]
        GEM --> ER[Enhanced Response]
    end

    MT --> TR[Tool Results]
    TR --> CE
    ER --> CI
    CI --> UD[User Display<br/>with Tool Badges]

    style U fill:#e1f5fe
    style CI fill:#b3e5fc
    style MT fill:#9c27b0,color:#fff
    style GEM fill:#4285f4,color:#fff
    style UD fill:#81c784
```

## Detailed MCP Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant IntentDetector
    participant MCPTools
    participant GeminiAI

    User->>Frontend: Ask financial question<br/>"Help me budget $5000"
    Frontend->>Backend: Send message via API
    Backend->>IntentDetector: Analyze message intent
    IntentDetector-->>Backend: Detected: "budget"

    Backend->>MCPTools: Execute budget_analyzer
    MCPTools-->>Backend: Return calculations

    Backend->>GeminiAI: Get AI insights
    GeminiAI-->>Backend: Enhanced response

    Backend-->>Frontend: Stream response +<br/>MCP tools metadata
    Frontend-->>User: Display answer with<br/>🔧 MCP Tools badges
```

## MCP Tools Categories

```mermaid
graph LR
    subgraph "MCP Financial Tools Suite"
        subgraph "Planning Tools"
            BT[Budget Tracker]
            SG[Savings Goals]
            RP[Retirement Planner]
        end

        subgraph "Investment Tools"
            PC[Portfolio Calculator]
            RA[Risk Analyzer]
            DD[Dividend Calculator]
        end

        subgraph "Tax & Loan Tools"
            TC[Tax Calculator]
            LC[Loan Calculator]
            MC[Mortgage Calculator]
        end

        subgraph "Analysis Tools"
            CF[Cash Flow Analyzer]
            EC[Expense Categorizer]
            FA[Financial Advisor]
        end
    end

    style BT fill:#4caf50,color:#fff
    style PC fill:#2196f3,color:#fff
    style TC fill:#ff9800,color:#fff
    style CF fill:#9c27b0,color:#fff
```

## Key Features

### 1. **Intent Detection**
- Automatically identifies user's financial needs
- Maps questions to appropriate MCP tools
- No manual tool selection needed

### 2. **MCP Tool Execution**
- 20+ specialized financial calculators
- Real-time computation
- Accurate financial modeling

### 3. **AI Enhancement**
- Gemini AI provides context
- Personalized explanations
- Actionable insights

### 4. **Visual Feedback**
- Purple badges show tools used
- Transparent process
- Build user trust

## Example Flow

**User asks:** "I want to save $10,000 in 2 years"

1. **Intent Detection** → Identifies "savings" intent
2. **MCP Tool** → Executes `savings_calculator`
3. **Calculation** → Monthly savings: $417
4. **AI Enhancement** → Suggests budget adjustments
5. **Display** → Shows answer with 🔧 Savings Calculator badge

## Benefits for Users

- **Transparent**: See which tools are being used
- **Accurate**: Professional financial calculations
- **Intelligent**: AI-enhanced recommendations
- **Fast**: Real-time tool execution
- **Comprehensive**: 20+ financial tools in one platform