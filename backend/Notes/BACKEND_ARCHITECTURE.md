# FinanceGPT Pro Backend Architecture

## 🏗️ System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Client]
        MOBILE[Mobile App]
        API_CLIENT[API Client]
    end

    subgraph "API Gateway Layer"
        FASTAPI[FastAPI Server<br/>Port: 8000]
        WS[WebSocket Server<br/>Port: 8000/ws]
    end

    subgraph "MCP Server Layer"
        MCP[MCP Core Server]
        MCP_WS[MCP WebSocket<br/>Port: 9001]
        MCP_HTTP[MCP HTTP<br/>Port: 9000]
    end

    subgraph "Core Components"
        AUTH[Security Manager<br/>JWT + Encryption]
        RESOURCE[Resource Manager<br/>Financial Data]
        TOOLS[Tools Manager<br/>14 Financial Tools]
        TRANSPORT[Transport Layer<br/>WebSocket + HTTP]
    end

    subgraph "Service Layer"
        USER_SVC[User Service]
        TXN_SVC[Transaction Service]
        ANALYTICS[Analytics Service]
        NOTIFY[Notification Service]
    end

    subgraph "Data Layer"
        DB[(SQLite Database)]
        MOCK[Mock Data Store]
        CACHE[In-Memory Cache]
    end

    subgraph "AI Integration"
        GEMINI[Google Gemini AI<br/>API Integration]
        INSIGHTS[Insight Generator]
        FRAUD[Fraud Detector]
    end

    WEB --> FASTAPI
    MOBILE --> FASTAPI
    API_CLIENT --> FASTAPI

    WEB -.->|Real-time| WS
    MOBILE -.->|Real-time| WS

    FASTAPI --> MCP
    WS --> MCP_WS

    MCP --> AUTH
    MCP --> RESOURCE
    MCP --> TOOLS
    MCP --> TRANSPORT

    RESOURCE --> USER_SVC
    RESOURCE --> TXN_SVC
    RESOURCE --> ANALYTICS
    RESOURCE --> NOTIFY

    USER_SVC --> DB
    TXN_SVC --> DB
    ANALYTICS --> DB

    MCP --> MOCK
    AUTH --> CACHE

    TOOLS --> GEMINI
    TOOLS --> INSIGHTS
    TOOLS --> FRAUD

    TRANSPORT --> MCP_HTTP
    TRANSPORT --> MCP_WS
```

## 📖 Understanding the Architecture (Natural Language Explanation)

### **The Big Picture**
Imagine FinanceGPT Pro as a sophisticated financial command center with multiple layers, each handling specific responsibilities. Let me walk you through how everything connects:

### **Layer 1: Client Layer (The Entry Points)**
This is where users interact with our system. Think of it as the "front doors" to our application:
- **Web Client**: Users accessing through a web browser
- **Mobile App**: Users on their phones
- **API Client**: Other applications or developers using our API directly

### **Layer 2: API Gateway Layer (The Reception Desk)**
When users arrive, they first meet our reception desk - the FastAPI server:
- **FastAPI Server (Port 8000)**: This is the main receptionist that handles all incoming requests. It's like a smart secretary that knows exactly where to route each request.
- **WebSocket Server (Port 8000/ws)**: This is a special live communication channel. Instead of the usual "ask-and-wait" approach, this allows real-time conversations - like having a phone line that stays open for instant updates.

### **Layer 3: MCP Server Layer (The Brain)**
MCP (Model Context Protocol) is the genius brain of our operation:
- **MCP Core Server**: The central intelligence that makes all decisions
- **MCP WebSocket (Port 9001)**: A dedicated real-time channel for MCP-specific communications
- **MCP HTTP (Port 9000)**: A traditional request-response channel for MCP

Think of MCP as the CEO's office - all important decisions flow through here.

### **Layer 4: Core Components (The Department Heads)**
These are the specialized managers reporting to the MCP:

1. **Security Manager (The Security Chief)**
   - Uses JWT tokens (like ID badges) to verify who you are
   - Encrypts sensitive data (like putting documents in a safe)
   - Ensures only authorized people access specific information

2. **Resource Manager (The Data Librarian)**
   - Knows where all financial data is stored
   - Retrieves accounts, transactions, and goals
   - Like a librarian who can quickly find any financial record you need

3. **Tools Manager (The Financial Expert)**
   - Has 14 specialized financial calculators and analyzers
   - Can calculate loans, detect fraud, analyze budgets
   - Like having 14 financial advisors on standby

4. **Transport Layer (The Communication Director)**
   - Manages how messages move between components
   - Handles both WebSocket (live) and HTTP (traditional) communications
   - Like the postal service within our system

### **Layer 5: Service Layer (The Workers)**
These services do the actual work:
- **User Service**: Manages user accounts, profiles, authentication
- **Transaction Service**: Processes all money movements, categorizes spending
- **Analytics Service**: Crunches numbers, generates reports, finds patterns
- **Notification Service**: Sends alerts, reminders, and important updates

### **Layer 6: Data Layer (The Storage)**
Where everything is saved:
- **SQLite Database**: The main filing cabinet for permanent records
- **Mock Data Store**: Test data for demonstrations (like sample documents)
- **In-Memory Cache**: Quick-access storage for frequently used data (like a desk drawer for items you use often)

### **Layer 7: AI Integration (The Intelligence)**
Our AI-powered smart features:
- **Google Gemini AI**: The artificial intelligence brain for understanding and generating insights
- **Insight Generator**: Creates personalized financial advice
- **Fraud Detector**: Watches for suspicious activities like a security camera

### **How Data Flows (The Journey of a Request)**

Let's follow a typical request through the system:

1. **User Action**: A user clicks "Show my transactions" on the web app
2. **Entry Point**: The request enters through the Web Client
3. **Reception**: FastAPI receives it at port 8000
4. **Routing**: FastAPI forwards it to the MCP Core Server
5. **Security Check**: MCP asks Security Manager "Is this user allowed?"
6. **Data Retrieval**: If approved, Resource Manager is asked to get the data
7. **Service Work**: Resource Manager tells Transaction Service "Get this user's transactions"
8. **Database Query**: Transaction Service pulls data from the SQLite Database
9. **Return Journey**: Data flows back through the same path
10. **Response**: User sees their transactions on screen

### **Real-Time Features (The Live Updates)**

For real-time features like fraud alerts:
1. Something happens (suspicious transaction detected)
2. Fraud Detector immediately notifies MCP
3. MCP broadcasts through both WebSocket channels
4. All connected users get instant notification
5. No polling or refreshing needed - it's instant!

### **The Special MCP Architecture**

What makes our MCP design special:
- **Centralized Intelligence**: All decisions flow through MCP, ensuring consistency
- **Dual Communication**: Both traditional (HTTP) and real-time (WebSocket) channels
- **Modular Design**: Each component has a specific job, making the system maintainable
- **Security First**: Every request is authenticated and authorized
- **AI-Powered**: Integrated AI for smart features, not just basic CRUD operations

Think of the entire system like a modern bank:
- Customers (Clients) enter through various doors (Web/Mobile/API)
- Reception (FastAPI) greets them
- The main office (MCP) processes their requests
- Various departments (Services) do the work
- Records are kept in the vault (Database)
- AI advisors (Gemini) provide intelligent insights
- Security (Auth Manager) watches everything
- And there's a live announcement system (WebSocket) for urgent updates

This architecture ensures that FinanceGPT Pro is not just functional but also secure, scalable, and intelligent - perfect for handling complex financial operations while providing real-time insights and protection.

## 📊 Request Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant MCP
    participant Security
    participant Resource
    participant Tools
    participant Database
    participant AI

    Client->>FastAPI: HTTP Request
    FastAPI->>MCP: Forward Request
    MCP->>Security: Authenticate
    Security-->>MCP: Auth Result

    alt Authentication Failed
        MCP-->>FastAPI: 401 Unauthorized
        FastAPI-->>Client: Error Response
    else Authentication Success
        MCP->>Resource: Process Request

        alt Resource Request
            Resource->>Database: Query Data
            Database-->>Resource: Result Set
            Resource-->>MCP: Formatted Data
        else Tool Execution
            MCP->>Tools: Execute Tool
            Tools->>AI: AI Processing
            AI-->>Tools: AI Result
            Tools-->>MCP: Tool Result
        end

        MCP-->>FastAPI: Response
        FastAPI-->>Client: JSON Response
    end
```

## 🔄 WebSocket Real-Time Flow

```mermaid
sequenceDiagram
    participant Client
    participant WebSocket
    participant MCP_WS
    participant EventBus
    participant Broadcast

    Client->>WebSocket: Connect /ws/{user_id}
    WebSocket->>Client: Connection Accepted

    Client->>MCP_WS: Connect ws://localhost:9001
    MCP_WS->>Client: Welcome Message

    loop Real-time Updates
        EventBus->>Broadcast: New Event
        Broadcast->>WebSocket: Send to User
        Broadcast->>MCP_WS: Send to MCP Clients
        WebSocket->>Client: Push Update
        MCP_WS->>Client: Push Update
    end

    Note over EventBus: Fraud Alert Triggered
    EventBus->>Broadcast: Fraud Alert
    Broadcast->>WebSocket: Urgent Alert
    WebSocket->>Client: Immediate Notification
```

## 🛠️ Component Architecture

```mermaid
graph LR
    subgraph "API Layer (api/)"
        MAIN[main.py<br/>FastAPI App]
        ROUTES[routers/<br/>Endpoints]
        SCHEMAS[schemas/<br/>Pydantic Models]
        DEPS[dependencies/<br/>Auth & DB]
    end

    subgraph "MCP Server (mcp_server/)"
        SERVER[server.py<br/>Core Server]
        PROTOCOL[protocol.py<br/>JSON-RPC]
        TRANS[transport.py<br/>WS + HTTP]
        SEC[security.py<br/>Auth & Crypto]
        RES[resources.py<br/>Data Access]
        TOOL[tools.py<br/>Financial Tools]
        MOCK_DATA[mock_data.py<br/>Test Data]
    end

    subgraph "Services (services/)"
        USER[user_service.py]
        TRANSACTION[transaction_service.py]
        ANALYTIC[analytics_service.py]
        NOTIFICATION[notification_service.py]
    end

    subgraph "Database (database/)"
        CONN[connection.py<br/>SQLAlchemy]
        INIT[init_db.py<br/>Setup]
    end

    subgraph "Models (models/)"
        U_MODEL[user.py]
        A_MODEL[account.py]
        T_MODEL[transaction.py]
        G_MODEL[goal.py]
        I_MODEL[investment.py]
        AL_MODEL[alert.py]
        IN_MODEL[insight.py]
        C_MODEL[chat.py]
    end

    subgraph "Utils (utils/)"
        VAL[validators.py<br/>Indian Validators]
        FMT[formatters.py<br/>Currency Format]
        HELP[helpers.py<br/>Calculations]
    end

    MAIN --> SERVER
    SERVER --> PROTOCOL
    SERVER --> TRANS
    SERVER --> SEC
    SERVER --> RES
    SERVER --> TOOL

    RES --> USER
    RES --> TRANSACTION
    RES --> ANALYTIC

    USER --> U_MODEL
    TRANSACTION --> T_MODEL
    ANALYTIC --> A_MODEL
```

## 🔐 Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        REQ[Incoming Request]

        RATE[Rate Limiting<br/>100 req/min]
        AUTH[Authentication<br/>JWT/API Key]
        AUTHZ[Authorization<br/>Role-Based]
        ENCRYPT[Encryption<br/>Fernet]
        SANITIZE[Output Sanitization]

        REQ --> RATE
        RATE --> AUTH
        AUTH --> AUTHZ
        AUTHZ --> ENCRYPT
        ENCRYPT --> PROCESS[Process Request]
        PROCESS --> SANITIZE
        SANITIZE --> RESP[Response]
    end

    subgraph "Security Features"
        JWT[JWT Tokens<br/>24hr expiry]
        SESSION[Session Management<br/>2hr timeout]
        APIKEY[API Keys<br/>Secure generation]
        HASH[Password Hashing<br/>SHA256]
        AUDIT[Audit Logging<br/>Security events]
    end

    AUTH --> JWT
    AUTH --> SESSION
    AUTH --> APIKEY
    AUTH --> HASH
    AUTHZ --> AUDIT
```

## 📁 Directory Structure

```
backend/
├── api/                    # FastAPI Application Layer
│   ├── main.py            # Main FastAPI app & endpoints
│   ├── routers/           # API route modules
│   ├── schemas/           # Pydantic models
│   └── dependencies/      # Shared dependencies
│
├── mcp_server/            # MCP Server Core
│   ├── server.py          # Main MCP server
│   ├── protocol.py        # JSON-RPC protocol handler
│   ├── transport.py       # WebSocket & HTTP transport
│   ├── security.py        # Authentication & encryption
│   ├── resources.py       # Resource manager
│   ├── tools.py           # 14 financial tools
│   └── mock_data.py       # Mock data generator
│
├── database/              # Database Layer
│   ├── connection.py      # SQLAlchemy setup
│   └── init_db.py         # Database initialization
│
├── models/                # SQLAlchemy Models
│   ├── user.py           # User model
│   ├── account.py        # Bank account model
│   ├── transaction.py    # Transaction model
│   ├── goal.py           # Financial goal model
│   ├── investment.py     # Investment model
│   ├── alert.py          # Alert model
│   ├── insight.py        # Insight model
│   └── chat.py           # Chat history model
│
├── services/              # Business Logic Layer
│   ├── user_service.py   # User management
│   ├── transaction_service.py  # Transaction processing
│   ├── analytics_service.py    # Analytics engine
│   └── notification_service.py # Alert system
│
├── utils/                 # Utility Functions
│   ├── validators.py      # Indian validators (PAN, Aadhar, etc.)
│   ├── formatters.py      # Currency formatters (Lakh/Crore)
│   └── helpers.py         # Calculation helpers
│
├── data/                  # Data Storage
│   └── mock/             # Mock JSON data files
│
├── tests/                 # Test Suite
│   ├── test_api.py       # API endpoint tests
│   └── test_gemini_api.py # Gemini integration test
│
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── run_api.py            # API startup script
└── run.py                # Full system startup
```

## 🚀 How Everything Works

### 1. **Startup Process**
```python
1. run_api.py starts
2. FastAPI app initializes (port 8000)
3. MCP Server initializes
4. MCP WebSocket starts (port 9001)
5. MCP HTTP starts (port 9000)
6. Mock data loads
7. Security manager initializes
8. Database connects
9. Services ready
```

### 2. **Request Processing Flow**

#### Standard API Request:
1. Client sends HTTP request to FastAPI (port 8000)
2. FastAPI validates request schema
3. Request forwarded to MCP server
4. MCP Security Manager authenticates
5. MCP routes to appropriate handler:
   - `resources.*` → Resource Manager
   - `tools.*` → Tools Manager
   - `system.*` → System Handler
6. Handler processes request:
   - Queries database/mock data
   - Executes calculations
   - Generates insights
7. Response formatted and returned
8. FastAPI sends JSON response to client

#### WebSocket Connection:
1. Client connects to `/ws/{user_id}` or `ws://localhost:9001`
2. Connection authenticated
3. Welcome message sent
4. Client can send real-time requests
5. Server broadcasts updates to all connected clients

### 3. **Key Components**

#### **MCP Server** (`mcp_server/server.py`)
- Central coordination point
- Handles all financial data requests
- Manages connections and sessions
- Routes requests to appropriate managers

#### **Security Manager** (`mcp_server/security.py`)
- JWT token generation/validation
- Session management
- API key handling
- Data encryption (Fernet)
- Rate limiting
- Fraud validation

#### **Resource Manager** (`mcp_server/resources.py`)
- Handles data CRUD operations
- Manages accounts, transactions, goals
- Aggregates financial data
- Provides filtered queries

#### **Tools Manager** (`mcp_server/tools.py`)
14 Financial Tools:
1. **Budget Analyzer** - Spending analysis
2. **Expense Tracker** - Track daily expenses
3. **Savings Calculator** - Savings goals
4. **Loan Calculator** - EMI calculations
5. **Investment Analyzer** - Portfolio analysis
6. **Tax Calculator** - Indian tax computation
7. **Retirement Planner** - Retirement savings
8. **Goal Optimizer** - Multi-goal planning
9. **Fraud Detector** - Transaction fraud detection
10. **Credit Analyzer** - Credit score analysis
11. **Bill Reminder** - Payment reminders
12. **Portfolio Optimizer** - Investment optimization
13. **Cash Flow Analyzer** - Income/expense patterns
14. **Insight Generator** - AI-powered insights

#### **Service Layer** (`services/`)
- **UserService**: Authentication, profile management
- **TransactionService**: Transaction processing, categorization
- **AnalyticsService**: Financial analytics, reports
- **NotificationService**: Alerts, notifications

### 4. **Data Flow**

```
Client Request → FastAPI → MCP Server → Security Check →
Route Handler → Service Layer → Database/Mock Data →
Process → Format Response → Return to Client
```

### 5. **Real-time Features**

#### Fraud Detection Demo:
1. Trigger endpoint called
2. MCP creates suspicious transaction
3. Fraud detector analyzes
4. Alert generated
5. Broadcast to all WebSocket clients
6. Immediate UI notification

#### Live Updates:
- Account balance changes
- New transactions
- Goal progress
- Investment updates
- System alerts

### 6. **AI Integration**

#### Gemini AI Integration:
- API Key: Stored in `.env`
- Used for insight generation
- Natural language processing
- Financial advice generation
- Pattern recognition

### 7. **Authentication Flow**

```
Login Request → Validate Credentials →
Generate JWT Token → Create Session →
Return Token + User Data →
Client stores token →
Subsequent requests include token →
Validate token on each request
```

### 8. **Demo Credentials**

| Email | Password | Role |
|-------|----------|------|
| demo@financegpt.com | Demo@123 | User |
| admin@financegpt.com | Admin@123 | Admin |

## 🔧 Configuration

### Environment Variables (.env):
```env
GEMINI_API_KEY=AIzaSyArVob6IeFoZjRIRe5aQuivtXjkSn9iMV8
DATABASE_URL=sqlite:///./financebot.db
JWT_SECRET=hackathon-secret-2025
ENVIRONMENT=development
```

### Server Ports:
- **FastAPI**: 8000
- **MCP WebSocket**: 9001
- **MCP HTTP**: 9000

## 🧪 Testing

### Test Coverage:
1. ✅ Health Check
2. ✅ Authentication (Login/Logout)
3. ✅ Account Management
4. ✅ Transaction Operations
5. ✅ Transaction Analysis
6. ✅ Financial Goals
7. ✅ Tool Listing
8. ✅ Tool Execution
9. ✅ Fraud Detection
10. ✅ Insight Generation
11. ✅ WebSocket Connection
12. ✅ MCP WebSocket
13. ✅ Fraud Demo Trigger

### Running Tests:
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python test_api.py

# Test Gemini integration
python test_gemini_api.py
```

## 🚦 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Accounts
- `GET /api/v1/accounts` - Get user accounts
- `POST /api/v1/accounts` - Create account

### Transactions
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/transactions` - Create transaction
- `POST /api/v1/transactions/analyze` - Analyze spending

### Financial Tools
- `GET /api/v1/tools` - List available tools
- `POST /api/v1/tools/execute` - Execute a tool

### Insights & AI
- `POST /api/v1/insights/generate` - Generate AI insights
- `POST /api/v1/fraud/check` - Check for fraud

### Real-time
- `WS /ws/{user_id}` - WebSocket connection
- `POST /api/v1/demo/trigger-fraud` - Trigger fraud demo

### System
- `GET /health` - Health check
- `GET /api/v1/system/info` - System information

## 🎯 Key Features

1. **MCP Architecture** - Model Context Protocol for AI-to-data communication
2. **Real-time Updates** - WebSocket for live data
3. **AI-Powered Insights** - Gemini integration
4. **Indian Context** - PAN, Aadhar, GST validators
5. **Fraud Detection** - Real-time transaction monitoring
6. **14 Financial Tools** - Comprehensive calculations
7. **Secure** - JWT, encryption, rate limiting
8. **Mock Data** - Ready for demos
9. **SQLAlchemy ORM** - Database abstraction
10. **FastAPI** - Modern, fast, async

## 🏆 Hackathon Highlights

### What Makes Us Different:
1. **MCP Server** - Unique architecture for AI-data interaction
2. **Dual WebSocket** - Both API and MCP WebSocket servers
3. **Indian Financial Context** - Localized for Indian users
4. **Real-time Fraud Detection** - Live demo capability
5. **14 Integrated Tools** - Complete financial toolkit
6. **Production-Ready Security** - Enterprise-grade security
7. **AI Integration** - Gemini for intelligent insights

### Demo Flow:
1. Show API documentation at `/docs`
2. Login with demo credentials
3. Display real-time account data
4. Execute financial tools
5. **Trigger fraud alert** - WOW moment!
6. Show AI-generated insights
7. Demonstrate WebSocket real-time updates

## 📝 Notes

- All timestamps in ISO format
- Currency in INR with Lakh/Crore formatting
- Mock data pre-loaded for demo
- Gemini API integrated but optional
- SQLite for zero-setup deployment
- Rate limiting: 100 requests/minute
- JWT tokens expire in 24 hours
- Sessions timeout in 2 hours

## 🔗 Quick Links

- API Docs: http://localhost:8000/docs
- API Base: http://localhost:8000
- WebSocket: ws://localhost:8000/ws/{user_id}
- MCP WebSocket: ws://localhost:9001

---

**Built for LJ Hackathon 2025** 🚀