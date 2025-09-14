#!/usr/bin/env python
"""
Test script for FinanceGPT Pro API
Verifies all endpoints are working correctly
"""

import asyncio
import httpx
import json
import websockets
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
MCP_WS_URL = "ws://localhost:9001"

# Test credentials
TEST_USER = {
    "email": "demo@financegpt.com",
    "password": "Demo@123"
}

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE_URL)
        self.token = None
        self.user_id = "USR001"

    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = await self.client.get("/health")
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Health Check: {data['status']}")
            return True
        except Exception as e:
            logger.error(f"❌ Health Check failed: {e}")
            return False

    async def test_login(self):
        """Test login endpoint"""
        try:
            response = await self.client.post(
                "/api/v1/auth/login",
                json=TEST_USER
            )
            assert response.status_code == 200
            data = response.json()
            self.token = data["token"]
            self.user_id = data["user"]["user_id"]
            logger.info(f"✅ Login successful: User {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False

    async def test_get_accounts(self):
        """Test accounts endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = await self.client.get(
                f"/api/v1/accounts?user_id={self.user_id}",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Accounts fetched: {len(data.get('accounts', []))} accounts")
            return True
        except Exception as e:
            logger.error(f"❌ Get accounts failed: {e}")
            return False

    async def test_get_transactions(self):
        """Test transactions endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = await self.client.get(
                f"/api/v1/transactions?user_id={self.user_id}&limit=10",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Transactions fetched: {len(data.get('transactions', []))} transactions")
            return True
        except Exception as e:
            logger.error(f"❌ Get transactions failed: {e}")
            return False

    async def test_analyze_transactions(self):
        """Test transaction analysis"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = await self.client.post(
                "/api/v1/transactions/analyze",
                json={"user_id": self.user_id, "period": "month"},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Transaction analysis: Total spent ₹{data.get('total_expense', 0):,.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Transaction analysis failed: {e}")
            return False

    async def test_goals(self):
        """Test goals endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = await self.client.get(
                f"/api/v1/goals?user_id={self.user_id}",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Goals fetched: {len(data.get('goals', []))} goals")
            return True
        except Exception as e:
            logger.error(f"❌ Get goals failed: {e}")
            return False

    async def test_tools_list(self):
        """Test tools listing"""
        try:
            response = await self.client.get("/api/v1/tools")
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Tools available: {len(data)} tools")
            return True
        except Exception as e:
            logger.error(f"❌ Tools list failed: {e}")
            return False

    async def test_tool_execution(self):
        """Test tool execution"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = await self.client.post(
                "/api/v1/tools/execute",
                json={
                    "tool_name": "budget_analyzer",
                    "parameters": {"period": "month"},
                    "user_id": self.user_id
                },
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Tool executed: Budget analysis completed")
            return True
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return False

    async def test_fraud_check(self):
        """Test fraud detection"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            test_transaction = {
                "id": "TEST001",
                "amount": -50000,
                "merchant": "Suspicious Merchant",
                "category": "OTHER",
                "date": datetime.now().isoformat()
            }
            response = await self.client.post(
                "/api/v1/fraud/check",
                json={
                    "transaction": test_transaction,
                    "user_id": self.user_id
                },
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Fraud check: Risk score {data.get('risk_score', 0)}/100")
            return True
        except Exception as e:
            logger.error(f"❌ Fraud check failed: {e}")
            return False

    async def test_insights(self):
        """Test insights generation"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = await self.client.post(
                "/api/v1/insights/generate",
                json={
                    "user_id": self.user_id,
                    "insight_type": "general"
                },
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Insights generated: {len(data.get('insights', []))} insights")
            return True
        except Exception as e:
            logger.error(f"❌ Insights generation failed: {e}")
            return False

    async def test_websocket(self):
        """Test WebSocket connection"""
        try:
            ws_url = f"{WS_URL}/{self.user_id}"
            async with websockets.connect(ws_url) as websocket:
                # Wait for connection message
                message = await websocket.recv()
                data = json.loads(message)
                assert data["type"] == "connection"

                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))

                # Wait for pong
                response = await websocket.recv()
                data = json.loads(response)
                assert data["type"] == "pong"

                logger.info("✅ WebSocket connection working")
                return True
        except Exception as e:
            logger.error(f"❌ WebSocket test failed: {e}")
            return False

    async def test_mcp_websocket(self):
        """Test MCP WebSocket connection"""
        try:
            async with websockets.connect(MCP_WS_URL) as websocket:
                # Wait for welcome message
                message = await websocket.recv()
                data = json.loads(message)
                assert data["type"] == "welcome"

                # Send a simple request
                request = {
                    "jsonrpc": "2.0",
                    "method": "system.ping",
                    "params": {},
                    "id": 1
                }
                await websocket.send(json.dumps(request))

                # Wait for response
                response = await websocket.recv()
                data = json.loads(response)

                logger.info("✅ MCP WebSocket connection working")
                return True
        except Exception as e:
            logger.error(f"❌ MCP WebSocket test failed: {e}")
            return False

    async def test_fraud_demo(self):
        """Test fraud demo trigger"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = await self.client.post(
                "/api/v1/demo/trigger-fraud",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            logger.info(f"✅ Fraud demo triggered: {data.get('alert', {}).get('title', 'Success')}")
            logger.info(f"   💰 Customer saved: {data.get('alert', {}).get('customer_saved', 'N/A')}")
            return True
        except Exception as e:
            logger.error(f"❌ Fraud demo failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all tests"""
        logger.info("\n" + "="*50)
        logger.info("🧪 Starting FinanceGPT Pro API Tests")
        logger.info("="*50 + "\n")

        tests = [
            ("Health Check", self.test_health_check),
            ("Login", self.test_login),
            ("Get Accounts", self.test_get_accounts),
            ("Get Transactions", self.test_get_transactions),
            ("Analyze Transactions", self.test_analyze_transactions),
            ("Get Goals", self.test_goals),
            ("List Tools", self.test_tools_list),
            ("Execute Tool", self.test_tool_execution),
            ("Fraud Check", self.test_fraud_check),
            ("Generate Insights", self.test_insights),
            ("WebSocket", self.test_websocket),
            ("MCP WebSocket", self.test_mcp_websocket),
            ("Fraud Demo", self.test_fraud_demo),
        ]

        results = []
        for name, test_func in tests:
            logger.info(f"\n🔍 Testing: {name}")
            try:
                result = await test_func()
                results.append((name, result))
            except Exception as e:
                logger.error(f"   Test error: {e}")
                results.append((name, False))

        # Summary
        logger.info("\n" + "="*50)
        logger.info("📊 Test Results Summary")
        logger.info("="*50)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {name}")

        logger.info(f"\n🎯 Total: {passed}/{total} tests passed")

        if passed == total:
            logger.info("🎉 All tests passed! API is ready for the hackathon!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Please check the logs.")

        await self.client.aclose()

async def main():
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())