#!/usr/bin/env python3
"""
Context7 STDIO Integration - Real implementation using stdio transport
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Context7StdioClient:
    """Context7 client using stdio transport (default mode)"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.response_queue = queue.Queue()
        self.reader_thread: Optional[threading.Thread] = None
        self.running = False
        self.tools = {}
        
    def start(self) -> bool:
        """Start Context7 MCP server with stdio transport"""
        try:
            # Start Context7 with default stdio transport
            cmd = ["npx", "-y", "@upstash/context7-mcp"]
            
            logger.info(f"🚀 Starting Context7 with stdio: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Start reader thread
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_responses)
            self.reader_thread.daemon = True
            self.reader_thread.start()
            
            # Initialize MCP connection
            if self._initialize():
                logger.info("✅ Context7 stdio client initialized")
                return True
            else:
                logger.error("❌ Failed to initialize Context7")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Context7: {e}")
            return False
            
    def _read_responses(self):
        """Read responses from stdout in separate thread"""
        while self.running and self.process:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line.startswith('{'):
                        try:
                            response = json.loads(line)
                            self.response_queue.put(response)
                        except json.JSONDecodeError:
                            logger.debug(f"Non-JSON output: {line}")
                            
            except Exception as e:
                logger.error(f"Reader error: {e}")
                break
                
    def _send_request(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send request via stdin and wait for response"""
        if not self.process or not self.running:
            logger.error("Process not running")
            return None
            
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id
        }
        
        try:
            # Send request
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
            
            logger.debug(f"📤 Sent: {method}")
            
            # Wait for response with matching ID
            timeout = 10  # seconds
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < timeout:
                try:
                    response = self.response_queue.get(timeout=0.1)
                    
                    # Check if this is our response
                    if response.get("id") == self.request_id:
                        logger.debug(f"📥 Received response for {method}")
                        return response
                        
                    # Put back if not our response
                    self.response_queue.put(response)
                    
                except queue.Empty:
                    continue
                    
            logger.error(f"Timeout waiting for response to {method}")
            return None
            
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
            
    def _send_notification(self, method: str, params: Dict[str, Any] = None):
        """Send notification (no response expected)"""
        if not self.process:
            return
            
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        try:
            notification_str = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_str)
            self.process.stdin.flush()
            logger.debug(f"📤 Sent notification: {method}")
        except Exception as e:
            logger.error(f"Notification error: {e}")
            
    def _initialize(self) -> bool:
        """Initialize MCP connection"""
        # Send initialize request
        response = self._send_request(
            "initialize",
            {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "Context7StdioClient",
                    "version": "1.0.0"
                }
            }
        )
        
        if response and "result" in response:
            # Send initialized notification
            self._send_notification("notifications/initialized")
            
            # List tools
            self._list_tools()
            return True
            
        return False
        
    def _list_tools(self):
        """List available tools"""
        response = self._send_request("tools/list")
        
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            for tool in tools:
                self.tools[tool["name"]] = tool
                logger.info(f"  📚 Tool: {tool['name']} - {tool['description']}")
                
    def enrich_context(self, input_text: str, libraries: List[str]) -> Optional[Dict[str, Any]]:
        """Enrich context with library documentation"""
        response = self._send_request(
            "tools/call",
            {
                "name": "enrich_context",
                "arguments": {
                    "input": input_text,
                    "libraries": libraries
                }
            }
        )
        
        if response and "result" in response:
            return response["result"]
            
        return None
        
    def stop(self):
        """Stop Context7 process"""
        self.running = False
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                
        logger.info("🛑 Context7 stopped")
        

class Context7RealIntegration:
    """Real Context7 integration for production use"""
    
    def __init__(self):
        self.client = Context7StdioClient()
        self.initialized = False
        
    def start(self) -> bool:
        """Start Context7 integration"""
        if self.client.start():
            self.initialized = True
            return True
        return False
        
    def enrich_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Enrich code with documentation"""
        if not self.initialized:
            return {"error": "Not initialized"}
            
        # Detect libraries
        libraries = self._detect_libraries(code, language)
        logger.info(f"📚 Detected libraries: {libraries}")
        
        # Get enrichment
        result = self.client.enrich_context(code, list(libraries))
        
        return {
            "success": result is not None,
            "libraries": list(libraries),
            "enrichment": result,
            "timestamp": datetime.now().isoformat()
        }
        
    def _detect_libraries(self, code: str, language: str) -> set:
        """Detect libraries in code"""
        libraries = set()
        
        if language == "python":
            for line in code.splitlines():
                line = line.strip()
                if line.startswith('import '):
                    parts = line.split()
                    if len(parts) > 1:
                        lib = parts[1].split('.')[0].split(' as ')[0]
                        libraries.add(lib)
                elif line.startswith('from '):
                    parts = line.split()
                    if len(parts) > 1:
                        lib = parts[1].split('.')[0]
                        libraries.add(lib)
                        
        elif language in ["javascript", "typescript"]:
            import re
            # ES6 imports
            for match in re.finditer(r'import\s+.*?\s+from\s+[\'"]([^\'\"]+)[\'"]', code):
                libraries.add(match.group(1))
            # CommonJS
            for match in re.finditer(r'require\([\'"]([^\'\"]+)[\'\"]', code):
                libraries.add(match.group(1))
                
        return libraries
        
    def stop(self):
        """Stop integration"""
        self.client.stop()
        

# Production-ready integration
def create_context7_integration() -> Context7RealIntegration:
    """Create production Context7 integration"""
    integration = Context7RealIntegration()
    if integration.start():
        return integration
    else:
        raise RuntimeError("Failed to start Context7")
        

# Test function
def test_context7_real():
    """Test real Context7 functionality"""
    logger.info("🧪 Testing Real Context7 Integration")
    logger.info("=" * 50)
    
    integration = Context7RealIntegration()
    
    try:
        # Start integration
        if not integration.start():
            logger.error("❌ Failed to start Context7")
            return
            
        # Test 1: Python code
        python_code = """
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load and prepare data
df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
"""
        
        logger.info("\n📝 Test 1: Python ML code")
        result = integration.enrich_code(python_code, "python")
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Libraries: {result['libraries']}")
        
        # Test 2: React code
        react_code = """
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Card } from 'antd';

export default function Dashboard() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchData();
    }, []);
    
    const fetchData = async () => {
        try {
            const response = await axios.get('/api/dashboard');
            setData(response.data);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <Card loading={loading}>
            <Button onClick={fetchData}>Refresh</Button>
        </Card>
    );
}
"""
        
        logger.info("\n📝 Test 2: React component")
        result = integration.enrich_code(react_code, "javascript")
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Libraries: {result['libraries']}")
        
        # Test 3: FastAPI code
        fastapi_code = """
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    
@app.post("/items")
async def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    return {"id": db_item.id, **item.dict()}
"""
        
        logger.info("\n📝 Test 3: FastAPI application")
        result = integration.enrich_code(fastapi_code, "python")
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Libraries: {result['libraries']}")
        
        if result.get("enrichment"):
            logger.info("\n📖 Enrichment sample:")
            enrichment = str(result["enrichment"])
            logger.info(f"  {enrichment[:200]}..." if len(enrichment) > 200 else f"  {enrichment}")
            
    finally:
        integration.stop()
        
    logger.info("\n✅ Context7 real integration test complete!")
    

if __name__ == "__main__":
    test_context7_real()