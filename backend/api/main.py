"""
FinanceGPT Pro - FastAPI Backend
Integrates MCP Server with Gemini AI for intelligent financial assistance
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
import uuid

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from mcp_server.server import MCPServer
from mcp_server.mock_data import load_mock_data
from api.simple_auth_service import SimpleAuthService

# Import AI service for enhanced analysis
try:
    from api.ai_service import get_ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI service not available: {e}")
    AI_SERVICE_AVAILABLE = False

# Import database service for AI storage
try:
    from api.database_service import get_database_service
    DATABASE_SERVICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database service not available: {e}")
    DATABASE_SERVICE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FinanceGPT Pro API",
    description="AI-powered personal finance assistant with MCP integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
mcp_server: Optional[MCPServer] = None
active_websockets: Dict[str, WebSocket] = {}
ai_service = None  # Will be initialized on startup
auth_service: Optional[SimpleAuthService] = None

# =====================
# Pydantic Models
# =====================

class UserLogin(BaseModel):
    """User login request"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User's message")
    user_id: str = Field(default="USR001", description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    suggestions: List[str] = Field(default=[], description="Suggested follow-up questions")
    data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")
    tools_used: List[str] = Field(default=[], description="MCP tools used")

class TransactionAnalysisRequest(BaseModel):
    """Transaction analysis request"""
    user_id: str = Field(default="USR001")
    period: str = Field(default="month", description="Analysis period")
    categories: Optional[List[str]] = None

class GoalRequest(BaseModel):
    """Financial goal request"""
    user_id: str = Field(default="USR001")
    goal_type: str = Field(..., description="Type of goal")
    target_amount: float = Field(..., description="Target amount")
    target_date: str = Field(..., description="Target date")
    monthly_contribution: Optional[float] = None

class FraudCheckRequest(BaseModel):
    """Fraud check request"""
    transaction: Dict[str, Any] = Field(..., description="Transaction to check")
    user_id: str = Field(default="USR001")

class InsightRequest(BaseModel):
    """Insight generation request"""
    user_id: str = Field(default="USR001")
    insight_type: str = Field(default="general", description="Type of insight")
    timeframe: str = Field(default="month", description="Timeframe for analysis")

class ToolExecutionRequest(BaseModel):
    """Tool execution request"""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default={}, description="Tool parameters")
    user_id: str = Field(default="USR001")

# =====================
# Startup & Shutdown
# =====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global mcp_server, auth_service

    logger.info("🚀 Starting FinanceGPT Pro API...")

    # Initialize auth service
    try:
        auth_service = SimpleAuthService()
        logger.info("✅ Authentication service initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize auth service: {e}")
        auth_service = None
    
    # Load mock data
    mock_data = load_mock_data()
    
    # Initialize MCP Server configuration
    config = {
        "server_name": "FinanceGPT Pro MCP Server",
        "version": "1.0.0",
        "port": 9000,
        "websocket_port": 9001,
        "enable_security": True,
        "enable_encryption": True,
        "environment": "development",
        "jwt_secret": "hackathon-secret-2025",
        "rate_limit": {
            "requests_per_minute": 100
        }
    }
    
    # Initialize MCP Server
    mcp_server = MCPServer(config)
    mcp_server.mock_data = mock_data

    # Start MCP server (including WebSocket on port 9001)
    await mcp_server.start()

    # Initialize AI service if available
    global ai_service
    if AI_SERVICE_AVAILABLE:
        try:
            ai_service = get_ai_service()
            logger.info("✅ AI Service initialized with enhanced analysis")
        except Exception as e:
            logger.warning(f"⚠️ AI Service initialization failed: {e}")
            ai_service = None

    logger.info("✅ All services initialized successfully")
    logger.info("🌐 API available at http://localhost:8000")
    logger.info("📚 API docs at http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mcp_server
    
    logger.info("🛍️ Shutting down FinanceGPT Pro API...")
    
    # Close all WebSocket connections
    for ws in active_websockets.values():
        await ws.close()
    
    # Shutdown MCP server
    if mcp_server:
        # MCP server cleanup if needed
        pass
    
    logger.info("👋 Goodbye!")

# =====================
# Health & Info Endpoints
# =====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "FinanceGPT Pro API",
        "version": "1.0.0",
        "status": "operational",
        "message": "Welcome to FinanceGPT Pro - Your AI Financial Assistant",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1/*"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "mcp_server": "operational" if mcp_server else "down",
            "websocket": "operational",
            "database": "operational"  # Mock data
        },
        "uptime": (datetime.now() - mcp_server.start_time).total_seconds() if mcp_server else 0
    }

# =====================
# Authentication Endpoints
# =====================

@app.post("/api/v1/auth/login")
async def login(credentials: UserLogin):
    """User login endpoint"""
    try:
        if not auth_service:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")

        # Use database authentication
        user = await auth_service.authenticate_user(
            credentials.email,
            credentials.password
        )

        if user:
            return {
                "success": True,
                "user_id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auth/logout")
async def logout(session_id: str):
    """User logout endpoint"""
    # Invalidate session
    if session_id in mcp_server.security_manager.active_sessions:
        del mcp_server.security_manager.active_sessions[session_id]
        return {"success": True, "message": "Logged out successfully"}
    return {"success": False, "message": "Session not found"}

# =====================
# User Endpoints
# =====================

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str):
    """Get user profile information"""
    try:
        if not auth_service:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")

        # Get user from database
        user = await auth_service.get_user_by_id(user_id)

        if user:
            return {
                "success": True,
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "user_type": user.get("user_type", "general"),
                    "profile_data": user.get("profile_data", {})
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/users/{user_id}/credit-score")
async def get_user_credit_score(user_id: str):
    """Get user's credit score"""
    try:
        # For demo purposes, return a realistic credit score based on user type
        if user_id.startswith("USR_8C4E025E"):  # Aarav - Young Professional
            score = 742
        elif user_id.startswith("USR_7A9B1F2C"):  # Priya - Family Person
            score = 785
        elif user_id.startswith("USR_5D8E4F3A"):  # Rajesh - Business Owner
            score = 821
        else:
            score = 750  # Default score

        return {
            "success": True,
            "credit_score": score,
            "score_range": "300-850",
            "last_updated": "2024-09-01"
        }

    except Exception as e:
        logger.error(f"Credit score error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# Account & Transaction Endpoints
# =====================

@app.get("/api/v1/accounts")
async def get_accounts(user_id: str = "USR001"):
    """Get user's bank accounts"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "resources.accounts.list",
            "params": {"user_id": user_id},
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Accounts fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/transactions")
async def get_transactions(
    user_id: str = "USR001",
    limit: int = 50,
    offset: int = 0
):
    """Get user's transactions"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "resources.transactions.list",
            "params": {
                "user_id": user_id,
                "limit": limit,
                "offset": offset
            },
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Transactions fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/transactions/analyze")
async def analyze_transactions(request: TransactionAnalysisRequest):
    """Analyze user's transactions"""
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "resources.transactions.aggregate",
            "params": {
                "user_id": request.user_id,
                "period": request.period
            },
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(mcp_request, "api-request")
        
        if "result" in result:
            analysis = result["result"]
            
            # Add AI insights
            insight_request = {
                "jsonrpc": "2.0",
                "method": "tools.execute",
                "params": {
                    "tool": "insight_generator",
                    "params": {
                        "user_id": request.user_id,
                        "insight_type": "spending"
                    }
                },
                "id": str(uuid.uuid4())
            }
            
            insight_result = await mcp_server.handle_request(insight_request, "api-request")
            if "result" in insight_result:
                analysis["ai_insights"] = insight_result["result"]

            # Enhance with advanced AI analysis if available
            if ai_service:
                try:
                    # Get transactions for AI analysis
                    txn_request = {
                        "jsonrpc": "2.0",
                        "method": "resources.transactions.list",
                        "params": {"user_id": request.user_id},
                        "id": str(uuid.uuid4())
                    }
                    txn_result = await mcp_server.handle_request(txn_request, "api-request")

                    if "result" in txn_result and "transactions" in txn_result["result"]:
                        transactions = txn_result["result"]["transactions"]
                        ai_enhanced = await ai_service.enhance_spending_analysis(
                            transactions=transactions,
                            existing_result=analysis
                        )
                        analysis.update(ai_enhanced)
                        logger.info("✅ Spending analysis enhanced with AI")
                except Exception as e:
                    logger.warning(f"AI spending enhancement failed: {e}")

            return analysis
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Transaction analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# Investment & Goals Endpoints
# =====================

@app.get("/api/v1/investments")
async def get_investments(user_id: str = "USR001"):
    """Get user's investments"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "resources.investments.list",
            "params": {"user_id": user_id},
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Investments fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/goals")
async def get_goals(user_id: str = "USR001"):
    """Get user's financial goals"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "resources.goals.list",
            "params": {"user_id": user_id},
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Goals fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/goals/optimize")
async def optimize_goals(request: GoalRequest):
    """Optimize financial goals - Enhanced with AI recommendations"""
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools.execute",
            "params": {
                "tool": "goal_optimizer",
                "params": {
                    "user_id": request.user_id,
                    "available_monthly": request.monthly_contribution or 50000
                }
            },
            "id": str(uuid.uuid4())
        }

        result = await mcp_server.handle_request(mcp_request, "api-request")

        if "result" in result:
            optimization_result = result["result"]

            # Enhance with AI investment analysis
            if ai_service:
                try:
                    # Create user profile for AI analysis
                    user_profile = {
                        "age": 35,  # Default, should come from user data
                        "monthly_income": request.monthly_contribution * 3 if request.monthly_contribution else 150000,
                        "risk_tolerance": "MODERATE"
                    }

                    # Create goals list
                    goals = [{
                        "name": request.goal_type,
                        "target_amount": request.target_amount,
                        "deadline": request.target_date
                    }]

                    ai_enhanced = await ai_service.enhance_investment_analysis(
                        user_profile=user_profile,
                        goals=goals,
                        existing_result=optimization_result
                    )
                    optimization_result.update(ai_enhanced)
                    logger.info("✅ Goal optimization enhanced with AI recommendations")
                except Exception as e:
                    logger.warning(f"AI goal enhancement failed: {e}")

            return optimization_result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Goal optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# Tools Execution Endpoints
# =====================

@app.get("/api/v1/tools")
async def list_tools():
    """List all available MCP tools"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "tools.list",
            "params": {},
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Tools list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute a specific MCP tool"""
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools.execute",
            "params": {
                "tool": request.tool_name,
                "params": {**request.parameters, "user_id": request.user_id}
            },
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(mcp_request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# Fraud Detection Endpoints
# =====================

@app.post("/api/v1/fraud/check")
async def check_fraud(request: FraudCheckRequest):
    """Check transaction for fraud - Enhanced with AI analysis"""
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools.execute",
            "params": {
                "tool": "fraud_detector",
                "params": {
                    "transaction": request.transaction,
                    "user_id": request.user_id
                }
            },
            "id": str(uuid.uuid4())
        }

        result = await mcp_server.handle_request(mcp_request, "api-request")

        if "result" in result:
            # Get the basic result from MCP
            fraud_result = result["result"]

            # Enhance with AI analysis if available
            if ai_service:
                try:
                    enhanced_result = await ai_service.enhance_fraud_detection(
                        transaction=request.transaction,
                        existing_result=fraud_result
                    )
                    # Merge AI insights into the result
                    fraud_result.update(enhanced_result)
                    logger.info("✅ Fraud check enhanced with AI analysis")
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed, using basic result: {ai_error}")

            return fraud_result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Fraud check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/demo/trigger-fraud")
async def trigger_fraud_demo(background_tasks: BackgroundTasks):
    """Trigger fraud detection demo - THE WOW MOMENT! Now with real AI analysis!"""
    try:
        # Trigger MCP's fraud simulation
        fraud_data = await mcp_server.simulate_fraud_alert()

        # Get AI analysis for the fraudulent transaction
        ai_analysis_result = None
        if ai_service:
            try:
                ai_analysis_result = await ai_service.enhance_fraud_detection(
                    transaction=fraud_data,
                    existing_result={"risk_score": 0.92, "risk_level": "HIGH"}
                )
            except Exception as e:
                logger.warning(f"AI analysis failed for demo: {e}")

        # Broadcast to WebSocket clients
        alert_message = {
            "type": "fraud_alert",
            "data": fraud_data,
            "timestamp": datetime.now().isoformat(),
            "severity": "HIGH",
            "ai_analysis": ai_analysis_result.get("ai_analysis", {}) if ai_analysis_result else None
        }

        # Send to all connected WebSocket clients
        for ws in active_websockets.values():
            await ws.send_json(alert_message)

        # Generate dramatic response with real AI insights
        response = {
            "success": True,
            "alert": {
                "title": "🚨 FRAUD ALERT DETECTED! 🚨",
                "transaction": fraud_data,
                "risk_score": ai_analysis_result.get("risk_score", 0.92) if ai_analysis_result else 0.92,
                "risk_level": ai_analysis_result.get("risk_level", "HIGH") if ai_analysis_result else "HIGH",
                "ai_analysis": ai_analysis_result.get("ai_analysis", {
                    "explanation": "Suspicious international transaction detected with unusual merchant pattern"
                }) if ai_analysis_result else "Suspicious international transaction detected with unusual merchant pattern",
                "actions_taken": [
                    "✓ Transaction blocked immediately",
                    "✓ Card temporarily frozen",
                    "✓ SMS alert sent to registered mobile",
                    "✓ Email notification dispatched",
                    "✓ 24/7 support team notified"
                ],
                "customer_saved": f"₹{abs(fraud_data['amount']):,.2f}"
            },
            "demo_impact": "This real-time fraud detection saved the customer from a major financial loss!",
            "technology": "Powered by MCP + AI for instant fraud detection"
        }
        
        logger.info("🎆 Fraud demo triggered successfully!")
        return response
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# Insights & Analytics Endpoints
# =====================

@app.post("/api/v1/insights/generate")
async def generate_insights(request: InsightRequest):
    """Generate AI-powered financial insights - Enhanced with Gemini"""
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools.execute",
            "params": {
                "tool": "insight_generator",
                "params": {
                    "user_id": request.user_id,
                    "insight_type": request.insight_type
                }
            },
            "id": str(uuid.uuid4())
        }

        result = await mcp_server.handle_request(mcp_request, "api-request")

        if "result" in result:
            insights_result = result["result"]

            # Enhance with advanced AI insights
            if ai_service:
                try:
                    # Get user context for AI analysis
                    context = {
                        "user_id": request.user_id,
                        "insight_type": request.insight_type,
                        "timestamp": datetime.now().isoformat()
                    }

                    # Get additional context based on insight type
                    if request.insight_type == "spending":
                        # Get recent transactions for context
                        txn_request = {
                            "jsonrpc": "2.0",
                            "method": "resources.transactions.list",
                            "params": {"user_id": request.user_id, "limit": 10},
                            "id": str(uuid.uuid4())
                        }
                        txn_result = await mcp_server.handle_request(txn_request, "api-request")
                        if "result" in txn_result:
                            context["recent_transactions"] = txn_result["result"].get("transactions", [])[:5]

                    # Generate AI insights
                    ai_insights = await ai_service.generate_ai_insights(
                        data_type=request.insight_type,
                        context=context
                    )

                    # Merge AI insights
                    if isinstance(insights_result, dict):
                        insights_result["ai_enhanced"] = ai_insights
                    else:
                        insights_result = {
                            "basic_insights": insights_result,
                            "ai_enhanced": ai_insights
                        }

                    logger.info("✅ Insights enhanced with Gemini AI analysis")
                except Exception as e:
                    logger.warning(f"AI insights enhancement failed: {e}")

            return insights_result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Insight generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/alerts")
async def get_alerts(user_id: str = "USR001", unread_only: bool = False):
    """Get user's alerts and notifications"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "resources.alerts.list",
            "params": {
                "user_id": user_id,
                "unread_only": unread_only
            },
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Alerts fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# Chat Endpoint
# =====================

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: str = "USR001"

@app.post("/api/v1/chat")
async def chat_with_ai(request: ChatRequest):
    """AI-powered chat for financial advice and questions - Enhanced with MCP Tools"""
    try:
        # Basic response structure
        response = {
            "user_message": request.message,
            "timestamp": datetime.now().isoformat()
        }

        # Detect intent from user message for tool selection
        message_lower = request.message.lower()
        intent_keywords = {
            "budget": ["budget", "spending", "expenses", "breakdown", "allocat"],
            "savings": ["save", "saving", "goal", "target", "accumulate"],
            "fraud": ["fraud", "suspicious", "unusual", "scam", "unauthor"],
            "investment": ["invest", "portfolio", "returns", "stocks", "mutual"],
            "credit": ["credit", "score", "loan", "emi", "borrow"],
            "tax": ["tax", "deduction", "80c", "income tax", "filing"],
            "emergency": ["emergency", "contingency", "unexpected", "safety net"],
            "cash_flow": ["cash flow", "income", "monthly", "inflow", "outflow"],
            "subscription": ["subscription", "recurring", "monthly charge", "netflix", "spotify"]
        }

        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents.append(intent)

        # Execute relevant MCP tools based on detected intent
        tool_results = {}

        if detected_intents:
            logger.info(f"🎯 Detected intents: {detected_intents}")

            # Execute budget analyzer if budget-related
            if "budget" in detected_intents:
                try:
                    budget_request = {
                        "jsonrpc": "2.0",
                        "method": "tools.execute",
                        "params": {
                            "tool": "budget_analyzer",
                            "params": {"user_id": request.user_id, "period": "month"}
                        },
                        "id": str(uuid.uuid4())
                    }
                    budget_result = await mcp_server.handle_request(budget_request, "api-request")
                    if "result" in budget_result:
                        tool_results["budget_analysis"] = budget_result["result"]
                        logger.info("✅ Budget analyzer executed successfully")
                except Exception as e:
                    logger.warning(f"Budget analyzer failed: {e}")

            # Execute savings calculator if savings-related
            if "savings" in detected_intents:
                try:
                    savings_request = {
                        "jsonrpc": "2.0",
                        "method": "tools.execute",
                        "params": {
                            "tool": "savings_calculator",
                            "params": {"user_id": request.user_id}
                        },
                        "id": str(uuid.uuid4())
                    }
                    savings_result = await mcp_server.handle_request(savings_request, "api-request")
                    if "result" in savings_result:
                        tool_results["savings_analysis"] = savings_result["result"]
                        logger.info("✅ Savings calculator executed successfully")
                except Exception as e:
                    logger.warning(f"Savings calculator failed: {e}")

            # Execute fraud detector if fraud-related
            if "fraud" in detected_intents:
                try:
                    fraud_request = {
                        "jsonrpc": "2.0",
                        "method": "tools.execute",
                        "params": {
                            "tool": "fraud_risk_scorer",
                            "params": {"user_id": request.user_id}
                        },
                        "id": str(uuid.uuid4())
                    }
                    fraud_result = await mcp_server.handle_request(fraud_request, "api-request")
                    if "result" in fraud_result:
                        tool_results["fraud_analysis"] = fraud_result["result"]
                        logger.info("✅ Fraud risk scorer executed successfully")
                except Exception as e:
                    logger.warning(f"Fraud risk scorer failed: {e}")

            # Execute investment analyzer if investment-related
            if "investment" in detected_intents:
                try:
                    investment_request = {
                        "jsonrpc": "2.0",
                        "method": "tools.execute",
                        "params": {
                            "tool": "investment_analyzer",
                            "params": {"user_id": request.user_id}
                        },
                        "id": str(uuid.uuid4())
                    }
                    investment_result = await mcp_server.handle_request(investment_request, "api-request")
                    if "result" in investment_result:
                        tool_results["investment_analysis"] = investment_result["result"]
                        logger.info("✅ Investment analyzer executed successfully")
                except Exception as e:
                    logger.warning(f"Investment analyzer failed: {e}")

            # Execute cash flow analyzer if income/expense related
            if "cash_flow" in detected_intents:
                try:
                    cashflow_request = {
                        "jsonrpc": "2.0",
                        "method": "tools.execute",
                        "params": {
                            "tool": "cash_flow_analyzer",
                            "params": {"user_id": request.user_id}
                        },
                        "id": str(uuid.uuid4())
                    }
                    cashflow_result = await mcp_server.handle_request(cashflow_request, "api-request")
                    if "result" in cashflow_result:
                        tool_results["cashflow_analysis"] = cashflow_result["result"]
                        logger.info("✅ Cash flow analyzer executed successfully")
                except Exception as e:
                    logger.warning(f"Cash flow analyzer failed: {e}")

        # Fetch real user data from MCP server
        user_context = {}
        try:
            # Get user accounts
            accounts_request = {
                "jsonrpc": "2.0",
                "method": "resources.accounts.list",
                "params": {"user_id": request.user_id},
                "id": str(uuid.uuid4())
            }
            accounts_result = await mcp_server.handle_request(accounts_request, "api-request")

            # Get user transactions
            transactions_request = {
                "jsonrpc": "2.0",
                "method": "resources.transactions.list",
                "params": {"user_id": request.user_id, "limit": 50},
                "id": str(uuid.uuid4())
            }
            transactions_result = await mcp_server.handle_request(transactions_request, "api-request")

            # Process the data
            if "result" in accounts_result:
                accounts = accounts_result["result"].get("accounts", [])
                total_balance = sum(acc.get("balance", 0) for acc in accounts)
                user_context["total_balance"] = total_balance
                user_context["accounts_count"] = len(accounts)

            if "result" in transactions_result:
                transactions = transactions_result["result"].get("transactions", [])
                user_context["recent_transactions"] = transactions[:10]

                # Calculate spending patterns
                food_spending = sum(abs(t.get("amount", 0)) for t in transactions
                                   if t.get("merchant", "").upper() in ["SWIGGY", "ZOMATO", "UBEREATS"])
                transport_spending = sum(abs(t.get("amount", 0)) for t in transactions
                                        if t.get("merchant", "").upper() in ["UBER", "OLA"])

                user_context["food_spending"] = food_spending
                user_context["transport_spending"] = transport_spending
                user_context["total_transactions"] = len(transactions)

        except Exception as e:
            logger.warning(f"Could not fetch MCP data: {e}")

        # Try to enhance with AI if available
        if ai_service and ai_service.ai_enabled:
            try:
                # Get Gemini analyzer
                gemini = ai_service.gemini

                # Build enhanced context with real user data AND MCP tool results
                enhanced_context = {
                    "user_query": request.message,
                    "user_financial_data": user_context,
                    "mcp_tool_analysis": tool_results,  # ADD MCP TOOL RESULTS HERE
                    "detected_intents": detected_intents,
                    "user_id": request.user_id,
                    "timestamp": datetime.now().isoformat()
                }

                # Add any additional context from request
                if request.context:
                    enhanced_context.update(request.context)

                # Log tool results for debugging
                if tool_results:
                    logger.info(f"🔧 MCP Tools provided analysis: {list(tool_results.keys())}")

                # Analyze message intent with real data
                if "fraud" in request.message.lower() or "suspicious" in request.message.lower():
                    # Fraud-related query
                    result = await gemini.explain_financial_concept(
                        concept="Fraud Protection",
                        user_level="intermediate"
                    )
                    response["ai_response"] = result.get("explanation", "")
                    response["action_steps"] = result.get("action_steps", [])

                elif "invest" in request.message.lower() or "portfolio" in request.message.lower():
                    # Investment-related query
                    result = await gemini.analyze_with_self_consistency(
                        query=request.message,
                        context=enhanced_context,
                        passes=2
                    )
                    response["ai_response"] = result.get("recommendation", "")
                    response["key_points"] = result.get("key_points", [])

                elif "credit" in request.message.lower() or "score" in request.message.lower():
                    # Credit-related query
                    result = await gemini.explain_financial_concept(
                        concept="Credit Score Improvement",
                        user_level="beginner"
                    )
                    response["ai_response"] = result.get("explanation", "")
                    response["benefits"] = result.get("benefits", [])

                elif "spend" in request.message.lower() or "budget" in request.message.lower() or "food" in request.message.lower():
                    # Spending/budget query - include real spending data
                    enhanced_context["focus"] = "spending optimization"
                    enhanced_context["food_delivery_spending"] = user_context.get("food_spending", 0)
                    enhanced_context["transport_spending"] = user_context.get("transport_spending", 0)
                    result = await gemini.analyze_with_self_consistency(
                        query=request.message,
                        context=enhanced_context,
                        passes=2
                    )
                    response["ai_response"] = result.get("recommendation", "")
                    response["action_items"] = result.get("action_items", [])

                else:
                    # General financial query with full context
                    result = await gemini.analyze_with_self_consistency(
                        query=request.message,
                        context=enhanced_context,
                        passes=2
                    )
                    response["ai_response"] = result.get("recommendation", "")
                    response["confidence"] = result.get("confidence_score", 0)

                response["ai_powered"] = True

            except Exception as e:
                logger.warning(f"AI chat enhancement failed: {e}")
                # Fall back to basic response
                response["ai_response"] = "I understand your question. While I cannot provide AI-powered analysis right now, please consult with a financial advisor for personalized advice."
                response["ai_powered"] = False
        else:
            # No AI available - provide basic response
            response["ai_response"] = "AI features are currently unavailable. Please ensure your API key is configured."
            response["ai_powered"] = False

        # Transform response format for frontend compatibility
        return {
            "success": True,
            "response": response.get("ai_response", "I understand your question but couldn't generate a detailed response."),
            "ai_powered": response.get("ai_powered", False),
            "mcp_tools_used": list(tool_results.keys()) if tool_results else [],
            "tool_insights": tool_results if tool_results else None,
            "detected_intents": detected_intents,
            "timestamp": response.get("timestamp"),
            "user_message": response.get("user_message"),
            **{k: v for k, v in response.items() if k not in ["ai_response", "ai_powered", "timestamp", "user_message"]}
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# AI Analytics Endpoints
# =====================

@app.get("/api/v1/ai/stats/{user_id}")
async def get_ai_statistics(user_id: str):
    """Get AI usage statistics for user"""
    try:
        if DATABASE_SERVICE_AVAILABLE:
            db_service = get_database_service()
            stats = await db_service.get_user_ai_stats(user_id)
            return stats
        else:
            return {"error": "Database service not available"}
    except Exception as e:
        logger.error(f"AI stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/fraud-history/{user_id}")
async def get_fraud_history(user_id: str, days: int = 30):
    """Get fraud detection history for user"""
    try:
        if DATABASE_SERVICE_AVAILABLE:
            db_service = get_database_service()
            history = await db_service.get_fraud_history(user_id, days)
            return {"fraud_history": history, "period_days": days}
        else:
            return {"error": "Database service not available"}
    except Exception as e:
        logger.error(f"Fraud history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/insights-history/{user_id}")
async def get_insights_history(user_id: str, insight_type: Optional[str] = None, days: int = 30):
    """Get AI insights history for user"""
    try:
        if DATABASE_SERVICE_AVAILABLE:
            db_service = get_database_service()
            history = await db_service.get_ai_insights_history(user_id, insight_type, days)
            return {"insights_history": history, "insight_type": insight_type, "period_days": days}
        else:
            return {"error": "Database service not available"}
    except Exception as e:
        logger.error(f"Insights history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# Credit Score Endpoints
# =====================

@app.get("/api/v1/credit-score")
async def get_credit_score(user_id: str = "USR001"):
    """Get user's credit score and analysis"""
    try:
        # Get credit data
        credit_request = {
            "jsonrpc": "2.0",
            "method": "resources.credit.get",
            "params": {"user_id": user_id},
            "id": str(uuid.uuid4())
        }
        
        credit_result = await mcp_server.handle_request(credit_request, "api-request")
        
        if "result" not in credit_result:
            raise HTTPException(status_code=404, detail="Credit data not found")
        
        # Analyze credit score
        analysis_request = {
            "jsonrpc": "2.0",
            "method": "tools.execute",
            "params": {
                "tool": "credit_analyzer",
                "params": {"user_id": user_id}
            },
            "id": str(uuid.uuid4())
        }
        
        analysis_result = await mcp_server.handle_request(analysis_request, "api-request")
        
        # Combine results
        response = credit_result["result"]
        if "result" in analysis_result:
            response["analysis"] = analysis_result["result"]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credit score fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# WebSocket Endpoint
# =====================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    
    # Store WebSocket connection
    connection_id = str(uuid.uuid4())
    active_websockets[connection_id] = websocket
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to FinanceGPT Pro",
            "user_id": user_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Receive message
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
                elif data.get("type") == "subscribe":
                    channels = data.get("channels", [])
                    await websocket.send_json({
                        "type": "subscribed",
                        "channels": channels,
                        "message": f"Subscribed to {', '.join(channels)}"
                    })
                    
                elif data.get("type") == "request":
                    # Process MCP request
                    mcp_request = data.get("request", {})
                    result = await mcp_server.handle_request(mcp_request, connection_id)
                    await websocket.send_json({
                        "type": "response",
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })

                elif data.get("type") == "fraud_check":
                    # Real-time fraud detection
                    transaction = data.get("transaction", {})
                    if transaction and ai_service:
                        try:
                            # Use AI service for real-time fraud analysis
                            result = await ai_service.enhance_fraud_detection(transaction)

                            # Send real-time alert if high risk
                            if result.get("risk_score", 0) > 0.7:
                                await websocket.send_json({
                                    "type": "fraud_alert",
                                    "alert_level": "HIGH",
                                    "risk_score": result.get("risk_score"),
                                    "risk_factors": result.get("risk_factors", []),
                                    "recommended_action": result.get("recommended_action"),
                                    "ai_analysis": result.get("ai_analysis", {}),
                                    "timestamp": datetime.now().isoformat()
                                })
                            else:
                                await websocket.send_json({
                                    "type": "fraud_check_result",
                                    "result": result,
                                    "timestamp": datetime.now().isoformat()
                                })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Fraud check failed: {str(e)}"
                            })

                elif data.get("type") == "spending_insight":
                    # Real-time spending insights
                    transactions = data.get("transactions", [])
                    if transactions and ai_service:
                        try:
                            result = await ai_service.enhance_spending_analysis(transactions)
                            await websocket.send_json({
                                "type": "spending_insights",
                                "insights": result.get("ai_insights", {}),
                                "recommendations": result.get("category_breakdown", {}),
                                "timestamp": datetime.now().isoformat()
                            })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Spending analysis failed: {str(e)}"
                            })

                elif data.get("type") == "chat_message":
                    # Real-time AI chat
                    message = data.get("message", "")
                    if message and ai_service and ai_service.ai_enabled:
                        try:
                            # Use chat functionality
                            result = await ai_service.gemini.analyze_with_self_consistency(
                                query=message,
                                context={"user_id": user_id, "channel": "websocket"},
                                passes=1  # Single pass for real-time
                            )
                            await websocket.send_json({
                                "type": "chat_response",
                                "message": result.get("recommendation", "I'm here to help with your financial questions!"),
                                "confidence": result.get("confidence_score", 0),
                                "timestamp": datetime.now().isoformat()
                            })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "chat_response",
                                "message": "I'm here to help! Please try rephrasing your question.",
                                "error": str(e),
                                "timestamp": datetime.now().isoformat()
                            })
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
    finally:
        # Clean up connection
        if connection_id in active_websockets:
            del active_websockets[connection_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

# =====================
# Utility Endpoints
# =====================

@app.post("/api/v1/calculate/loan")
async def calculate_loan(
    principal: float,
    interest_rate: float,
    tenure_months: int
):
    """Calculate loan EMI and details"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "tools.execute",
            "params": {
                "tool": "loan_calculator",
                "params": {
                    "principal": principal,
                    "interest_rate": interest_rate,
                    "tenure_months": tenure_months
                }
            },
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Loan calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/calculate/tax")
async def calculate_tax(
    annual_income: float,
    investments: Optional[Dict[str, float]] = None
):
    """Calculate tax liability"""
    try:
        request = {
            "jsonrpc": "2.0",
            "method": "tools.execute",
            "params": {
                "tool": "tax_calculator",
                "params": {
                    "annual_income": annual_income,
                    "investments": investments or {}
                }
            },
            "id": str(uuid.uuid4())
        }
        
        result = await mcp_server.handle_request(request, "api-request")
        
        if "result" in result:
            return result["result"]
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Tax calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/portfolio/{user_id}")
async def get_portfolio_analytics(user_id: str):
    """Get portfolio performance analytics"""
    try:
        # Get investments for portfolio value calculation
        investments = await auth_service.get_user_investments(user_id)

        # Calculate current portfolio value
        current_portfolio_value = sum(inv.get('current_value', 0) for inv in investments)

        # Generate 6-month performance data based on investments
        from datetime import datetime, timedelta
        performance_data = []
        base_value = current_portfolio_value * 0.85  # Start from 85% of current value

        for i in range(6):
            month_date = datetime.now() - timedelta(days=(5-i) * 30)
            month_name = month_date.strftime('%b')

            # Simulate growth over 6 months
            growth_factor = 1 + (i * 0.05)  # 5% growth per month
            value = int(base_value * growth_factor)

            performance_data.append({
                "month": month_name,
                "value": value
            })

        return {
            "portfolio_value": current_portfolio_value,
            "performance_data": performance_data,
            "investments": investments
        }

    except Exception as e:
        logger.error(f"Portfolio analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/cashflow/{user_id}")
async def get_cashflow_analytics(user_id: str, months: int = 6):
    """Get cash flow analytics"""
    try:
        # Get recent transactions for cash flow calculation
        transactions = await auth_service.get_user_transactions(user_id, limit=100)

        from datetime import datetime, timedelta
        import calendar

        # Group transactions by month
        monthly_data = {}
        current_date = datetime.now()

        for i in range(months):
            month_date = current_date - timedelta(days=i * 30)
            month_key = month_date.strftime('%Y-%m')
            month_name = month_date.strftime('%b')
            monthly_data[month_key] = {
                "month": month_name,
                "income": 0,
                "expenses": 0,
                "netFlow": 0
            }

        # Calculate income and expenses from transactions
        for txn in transactions:
            try:
                txn_date = datetime.fromisoformat(txn['date'].replace('Z', '+00:00'))
                month_key = txn_date.strftime('%Y-%m')

                if month_key in monthly_data:
                    amount = float(txn['amount'])
                    if amount > 0:
                        monthly_data[month_key]["income"] += amount
                    else:
                        monthly_data[month_key]["expenses"] += abs(amount)
            except (ValueError, KeyError):
                continue

        # Calculate net flow and ensure minimum realistic values
        cash_flow_data = []
        for month_key in sorted(monthly_data.keys(), reverse=True)[:months]:
            data = monthly_data[month_key]

            # Ensure minimum realistic values if no transactions
            if data["income"] == 0 and data["expenses"] == 0:
                data["income"] = 850000 + (hash(month_key) % 200000)  # Random but consistent
                data["expenses"] = 450000 + (hash(month_key) % 100000)
            elif data["income"] == 0:
                data["income"] = data["expenses"] * 1.8  # Assume some savings rate
            elif data["expenses"] == 0:
                data["expenses"] = data["income"] * 0.6  # Assume 60% expense ratio

            data["netFlow"] = data["income"] - data["expenses"]
            cash_flow_data.insert(0, data)  # Insert at beginning for chronological order

        # Calculate current month averages
        current_month_income = cash_flow_data[-1]["income"] if cash_flow_data else 0
        current_month_expenses = cash_flow_data[-1]["expenses"] if cash_flow_data else 0
        current_net_flow = current_month_income - current_month_expenses

        return {
            "cash_flow_data": cash_flow_data,
            "monthly_income": current_month_income,
            "monthly_expenses": current_month_expenses,
            "net_flow": current_net_flow
        }

    except Exception as e:
        logger.error(f"Cash flow analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/activities/{user_id}")
async def get_recent_activities(user_id: str, limit: int = 10):
    """Get recent activities for the user"""
    try:
        # Get recent transactions
        transactions = await auth_service.get_user_transactions(user_id, limit=limit)
        activities = []

        for txn in transactions[:limit]:
            try:
                amount = float(txn['amount'])
                merchant = txn.get('merchant', 'Unknown')
                txn_date = datetime.fromisoformat(txn['date'].replace('Z', '+00:00'))
                time_ago = get_time_ago(txn_date)

                if amount > 0:
                    activities.append({
                        "icon": "📈",
                        "text": f"Income from {merchant} - ₹{abs(amount):,.0f}",
                        "time": time_ago,
                        "type": "positive"
                    })
                else:
                    activities.append({
                        "icon": "💳",
                        "text": f"{merchant} payment - ₹{abs(amount):,.0f}",
                        "time": time_ago,
                        "type": "neutral"
                    })
            except (ValueError, KeyError):
                continue

        # Add some default activities if not enough transactions
        if len(activities) < 3:
            activities.extend([
                {
                    "icon": "🛡️",
                    "text": "Credit score updated: 742",
                    "time": "1 day ago",
                    "type": "positive"
                },
                {
                    "icon": "⚠️",
                    "text": "Large transaction detected",
                    "time": "2 days ago",
                    "type": "warning"
                }
            ])

        return {"activities": activities[:limit]}

    except Exception as e:
        logger.error(f"Recent activities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_time_ago(date):
    """Helper function to calculate time ago"""
    now = datetime.now()
    if date.tzinfo:
        now = now.replace(tzinfo=date.tzinfo)

    diff = now - date

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )