# MCP Architecture - Visual Guide

## 🎯 MCP Coordination Overview

```mermaid
graph TB
    subgraph "External World"
        USER[👤 User]
        GEMINI[🤖 Google Gemini AI]
    end

    subgraph "Entry Layer"
        API[FastAPI<br/>Port 8000]
        WS_API[WebSocket<br/>Port 8000/ws]
    end

    subgraph "MCP Core - The Coordinator"
        MCP_MAIN[🎛️ MCP Protocol Server]

        subgraph "MCP Components"
            SEC[🔐 Security Manager]
            PROTO[📋 Protocol Handler]
            TRANS[📡 Transport Layer]
        end
    end

    subgraph "What MCP Coordinates - Internal Tools"
        subgraph "14 Financial Tools"
            TOOL1[💰 Budget Analyzer]
            TOOL2[📊 Expense Tracker]
            TOOL3[🏦 Savings Calculator]
            TOOL4[🏠 Loan Calculator]
            TOOL5[📈 Investment Analyzer]
            TOOL6[💸 Tax Calculator]
            TOOL7[🏖️ Retirement Planner]
            TOOL8[🎯 Goal Optimizer]
            TOOL9[🚨 Fraud Detector]
            TOOL10[📉 Credit Analyzer]
            TOOL11[📅 Bill Reminder]
            TOOL12[💼 Portfolio Optimizer]
            TOOL13[💵 Cash Flow Analyzer]
            TOOL14[🧠 Insight Generator]
        end
    end

    subgraph "What MCP Manages - Data Resources"
        subgraph "8 Data Resources"
            RES1[🏦 Accounts]
            RES2[💳 Transactions]
            RES3[📈 Investments]
            RES4[🎯 Goals]
            RES5[🔔 Alerts]
            RES6[💡 Insights]
            RES7[📊 Credit Data]
            RES8[💼 EPF Data]
        end
    end

    subgraph "Data Storage"
        DB[(SQLite DB)]
        MOCK[Mock Data]
        CACHE[Redis Cache<br/>Future]
    end

    USER -->|Request| API
    API -->|Protocol| MCP_MAIN
    MCP_MAIN -->|Authenticate| SEC
    MCP_MAIN -->|Validate| PROTO
    MCP_MAIN -->|Route| TRANS

    MCP_MAIN -->|Execute| TOOL1
    MCP_MAIN -->|Execute| TOOL2
    MCP_MAIN -->|Execute| TOOL3
    MCP_MAIN -.->|Coordinates All 14| TOOL14

    MCP_MAIN -->|Access| RES1
    MCP_MAIN -->|Access| RES2
    MCP_MAIN -.->|Manages All 8| RES8

    TOOL14 -->|Uses| GEMINI
    TOOL9 -->|Analyzes| RES2

    RES1 --> DB
    RES2 --> DB
    RES1 --> MOCK
    RES2 --> MOCK

    style MCP_MAIN fill:#ff9999,stroke:#333,stroke-width:4px
    style USER fill:#99ccff,stroke:#333,stroke-width:2px
    style GEMINI fill:#99ff99,stroke:#333,stroke-width:2px
```

## 🔄 Request Flow Through MCP

```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant MCP
    participant Security
    participant Router
    participant Tool/Resource
    participant Database
    participant Gemini

    User->>FastAPI: "Calculate my loan EMI"
    FastAPI->>MCP: Forward Request (JSON-RPC)

    Note over MCP: MCP Coordination Begins

    MCP->>Security: Verify JWT Token
    Security-->>MCP: ✅ Authenticated

    MCP->>Router: Route to "tools.loan_calculator"
    Router->>Tool/Resource: Execute Loan Calculator

    Tool/Resource->>Database: Get User Data
    Database-->>Tool/Resource: User Financial Info

    Tool/Resource->>Tool/Resource: Calculate EMI<br/>Principal: ₹10L<br/>Interest: 8.5%<br/>Tenure: 240 months

    Tool/Resource-->>MCP: EMI: ₹8,678
    MCP-->>FastAPI: Formatted Response
    FastAPI-->>User: "Your EMI is ₹8,678"
```

## 🏗️ MCP as Central Coordinator

```mermaid
graph LR
    subgraph "Without MCP - Chaos"
        U1[User Request]
        U1 --> T1[Tool 1]
        U1 --> T2[Tool 2]
        U1 --> T3[Tool 3]
        U1 --> D1[Data 1]
        U1 --> D2[Data 2]
        T1 --> AUTH1[Auth]
        T2 --> AUTH2[Auth]
        T3 --> AUTH3[Auth]

        style U1 fill:#ffcccc
    end

    subgraph "With MCP - Organized"
        U2[User Request]
        U2 --> MCP[MCP Server]
        MCP --> AUTH[Single Auth]
        MCP --> TOOLS[All Tools]
        MCP --> DATA[All Data]

        style MCP fill:#99ff99,stroke:#333,stroke-width:3px
        style U2 fill:#ccffcc
    end
```

## 🎮 MCP Internal Tools Interaction

```mermaid
graph TB
    subgraph "MCP Tool Ecosystem"
        MCP_CORE[MCP Core]

        subgraph "Analysis Tools"
            BUDGET[Budget Analyzer]
            EXPENSE[Expense Tracker]
            CASHFLOW[Cash Flow Analyzer]
        end

        subgraph "Planning Tools"
            SAVINGS[Savings Calculator]
            RETIREMENT[Retirement Planner]
            GOALS[Goal Optimizer]
        end

        subgraph "Calculation Tools"
            LOAN[Loan Calculator]
            TAX[Tax Calculator]
            PORTFOLIO[Portfolio Optimizer]
        end

        subgraph "Security Tools"
            FRAUD[Fraud Detector]
            CREDIT[Credit Analyzer]
        end

        subgraph "AI Tools"
            INSIGHTS[Insight Generator]
            INSIGHTS --> GEMINI[Gemini AI]
        end

        subgraph "Utility Tools"
            REMINDER[Bill Reminder]
            INVEST[Investment Analyzer]
        end
    end

    MCP_CORE ==>|Coordinates| BUDGET
    MCP_CORE ==>|Coordinates| EXPENSE
    MCP_CORE ==>|Coordinates| SAVINGS
    MCP_CORE ==>|Coordinates| LOAN
    MCP_CORE ==>|Coordinates| FRAUD
    MCP_CORE ==>|Coordinates| INSIGHTS

    BUDGET -.->|Shares Data| EXPENSE
    EXPENSE -.->|Feeds Into| CASHFLOW
    CASHFLOW -.->|Informs| SAVINGS
    SAVINGS -.->|Helps| GOALS
    FRAUD -.->|Alerts| CREDIT

    style MCP_CORE fill:#ff9999,stroke:#333,stroke-width:4px
    style GEMINI fill:#99ff99,stroke:#333,stroke-width:2px
```

## 📊 MCP Resource Management

```mermaid
graph TB
    subgraph "MCP Resource Layer"
        MCP[MCP Server]

        subgraph "User Resources"
            ACCOUNTS[Accounts<br/>• Savings<br/>• Current<br/>• Credit]
            TRANS[Transactions<br/>• Deposits<br/>• Withdrawals<br/>• Transfers]
        end

        subgraph "Financial Resources"
            INVEST[Investments<br/>• Stocks<br/>• Mutual Funds<br/>• FDs]
            GOALS[Goals<br/>• Short-term<br/>• Long-term<br/>• Emergency]
        end

        subgraph "Intelligence Resources"
            INSIGHTS[Insights<br/>• AI Generated<br/>• Patterns<br/>• Recommendations]
            ALERTS[Alerts<br/>• Fraud<br/>• Bills<br/>• Goals]
        end

        subgraph "Credit Resources"
            CREDIT[Credit Data<br/>• Score<br/>• History<br/>• Loans]
            EPF[EPF Data<br/>• Balance<br/>• Contributions<br/>• Interest]
        end
    end

    subgraph "Data Sources"
        MOCK_DATA[Mock JSON Files]
        SQL_DB[SQLite Database]
        FUTURE_API[Future: Bank APIs]
    end

    MCP -->|Manages| ACCOUNTS
    MCP -->|Manages| TRANS
    MCP -->|Manages| INVEST
    MCP -->|Manages| GOALS
    MCP -->|Manages| INSIGHTS
    MCP -->|Manages| ALERTS
    MCP -->|Manages| CREDIT
    MCP -->|Manages| EPF

    ACCOUNTS --> MOCK_DATA
    ACCOUNTS --> SQL_DB
    TRANS --> MOCK_DATA
    TRANS --> SQL_DB

    FUTURE_API -.->|Future Integration| MCP

    style MCP fill:#ff9999,stroke:#333,stroke-width:4px
    style FUTURE_API fill:#ffff99,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
```

## 🔐 MCP Security Flow

```mermaid
graph LR
    subgraph "Request Journey Through MCP"
        REQ[Incoming Request]

        subgraph "MCP Security Layers"
            L1[Layer 1<br/>Rate Limiting]
            L2[Layer 2<br/>JWT Validation]
            L3[Layer 3<br/>Permission Check]
            L4[Layer 4<br/>Data Encryption]
        end

        EXEC[Execute Tool/Resource]
        RESP[Response]
    end

    REQ --> L1
    L1 -->|Pass| L2
    L1 -->|Fail| REJECT1[429 Too Many Requests]

    L2 -->|Valid| L3
    L2 -->|Invalid| REJECT2[401 Unauthorized]

    L3 -->|Allowed| L4
    L3 -->|Denied| REJECT3[403 Forbidden]

    L4 -->|Secure| EXEC
    EXEC --> RESP

    style L1 fill:#ffcccc
    style L2 fill:#ffffcc
    style L3 fill:#ccffcc
    style L4 fill:#ccccff
```

## 🌟 What MCP Currently Does vs Future

```mermaid
graph TB
    subgraph "Current Implementation"
        subgraph "Internal Tools & Data"
            CURR_MCP[MCP Server]
            CURR_TOOLS[14 Financial Tools<br/>All Internal]
            CURR_DATA[Mock Data<br/>SQLite DB]
            CURR_AI[Gemini AI<br/>For Insights]
        end

        CURR_MCP --> CURR_TOOLS
        CURR_MCP --> CURR_DATA
        CURR_TOOLS --> CURR_AI
    end

    subgraph "Future Potential"
        subgraph "External Integrations"
            FUT_MCP[Enhanced MCP]
            FUT_BANKS[Real Banks<br/>• ICICI<br/>• HDFC<br/>• SBI]
            FUT_PAY[Payment Gateways<br/>• Razorpay<br/>• Paytm<br/>• PhonePe]
            FUT_MARKET[Stock APIs<br/>• NSE<br/>• BSE<br/>• Zerodha]
            FUT_GOV[Government<br/>• Income Tax<br/>• PAN<br/>• Aadhar]
            FUT_CREDIT[Credit Bureaus<br/>• CIBIL<br/>• Experian]
        end

        FUT_MCP --> FUT_BANKS
        FUT_MCP --> FUT_PAY
        FUT_MCP --> FUT_MARKET
        FUT_MCP --> FUT_GOV
        FUT_MCP --> FUT_CREDIT
    end

    CURR_MCP -.->|Evolution| FUT_MCP

    style CURR_MCP fill:#99ff99,stroke:#333,stroke-width:3px
    style FUT_MCP fill:#ffff99,stroke:#333,stroke-width:3px,stroke-dasharray: 5 5
```

## 💡 Simple Analogy

```mermaid
graph TD
    subgraph "MCP is like a Smart Assistant"
        BOSS[You<br/>The User]

        ASSISTANT[MCP<br/>Smart Assistant]

        subgraph "Assistant's Desk Tools"
            CALC[Calculator<br/>Loan/Tax/Savings]
            LEDGER[Ledger Book<br/>Accounts/Transactions]
            ANALYZER[Analysis Tools<br/>Budget/Fraud/Credit]
            PLANNER[Planning Tools<br/>Goals/Retirement]
            AI_BRAIN[AI Brain<br/>Gemini Integration]
        end

        BOSS -->|"Calculate my EMI"| ASSISTANT
        ASSISTANT -->|Uses| CALC

        BOSS -->|"Show transactions"| ASSISTANT
        ASSISTANT -->|Checks| LEDGER

        BOSS -->|"Am I overspending?"| ASSISTANT
        ASSISTANT -->|Analyzes with| ANALYZER

        BOSS -->|"Plan my retirement"| ASSISTANT
        ASSISTANT -->|Plans with| PLANNER

        BOSS -->|"Give me insights"| ASSISTANT
        ASSISTANT -->|Thinks with| AI_BRAIN
    end

    style ASSISTANT fill:#ff9999,stroke:#333,stroke-width:4px
    style AI_BRAIN fill:#99ff99
```

## 🎯 The Key Point

**MCP is NOT connecting to external services. It's coordinating YOUR OWN internal tools and data.**

Think of MCP as:
- 🎛️ **Control Panel** for all your financial tools
- 🔐 **Security Guard** checking every request
- 📋 **Protocol Manager** ensuring standard communication
- 🚦 **Traffic Controller** routing requests to the right tool
- 📊 **Data Coordinator** managing access to your resources

**Current Reality**: MCP manages 14 tools + 8 resources (all internal)
**Future Potential**: MCP could manage external bank APIs, payment gateways, etc.

But right now, it's your **internal financial command center**, not an external service connector!