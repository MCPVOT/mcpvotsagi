
#!/usr/bin/env python3
"""
Enhanced Claudia API Server with Claude Sonnet 4 and Opus 4
"""

import asyncio
import json
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import anthropic
from claudia_usage_monitor import ClaudiaUsageMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClaudiaAdvancedAPI")

# Initialize FastAPI app
app = FastAPI(title="Claudia Advanced API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude clients
anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Initialize usage monitor
usage_monitor = ClaudiaUsageMonitor()

# Model configuration
MODEL_CONFIG = {
    "claude-3-opus-4": {
        "max_tokens": 4096,
        "temperature": 0.1,
        "cost_per_token": 0.000075  # Example cost
    },
    "claude-3-sonnet-4": {
        "max_tokens": 4096,
        "temperature": 0.2,
        "cost_per_token": 0.000015  # Example cost
    },
    "claude-3-haiku-20240307": {
        "max_tokens": 2048,
        "temperature": 0.3,
        "cost_per_token": 0.000001  # Example cost
    }
}

class ChatRequest(BaseModel):
    message: str
    task_type: str = "general"
    preferred_model: Optional[str] = None
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int
    cost: float
    timestamp: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_claudia(request: ChatRequest):
    """Enhanced chat endpoint with smart model selection"""
    try:
        # Optimize model selection
        if request.preferred_model:
            model = request.preferred_model
        else:
            model = await usage_monitor.optimize_model_selection(request.task_type)

        # Check model limits
        limit_check = await usage_monitor.check_model_limits(model)
        if limit_check["should_switch"]:
            model = limit_check["recommended_model"]

        # Create enhanced prompt
        enhanced_prompt = f"""
Task Type: {request.task_type}
Context: {json.dumps(request.context or {})}
User Message: {request.message}

As Claudia CC (Advanced), please provide a comprehensive response using {model} capabilities.
"""

        # Make API call to Claude
        message = anthropic_client.messages.create(
            model=model,
            max_tokens=MODEL_CONFIG[model]["max_tokens"],
            temperature=MODEL_CONFIG[model]["temperature"],
            messages=[{
                "role": "user",
                "content": enhanced_prompt
            }]
        )

        # Calculate cost
        tokens_used = message.usage.input_tokens + message.usage.output_tokens
        cost = tokens_used * MODEL_CONFIG[model]["cost_per_token"]

        return ChatResponse(
            response=message.content[0].text,
            model_used=model,
            tokens_used=tokens_used,
            cost=cost,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/usage/current")
async def get_current_usage():
    """Get current usage statistics"""
    try:
        usage_data = await usage_monitor.get_current_usage()
        return usage_data
    except Exception as e:
        logger.error(f"Error getting usage data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/status")
async def get_model_status():
    """Get status of all available models"""
    try:
        model_status = {}
        for model_name in MODEL_CONFIG.keys():
            limit_check = await usage_monitor.check_model_limits(model_name)
            model_status[model_name] = {
                "available": not limit_check["should_switch"],
                "usage_percentage": limit_check["usage_percentage"],
                "config": MODEL_CONFIG[model_name]
            }
        return model_status
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/jupiter")
async def analyze_jupiter_integration(request: Dict):
    """Specialized endpoint for Jupiter DEX analysis"""
    try:
        # Use Opus 4 for complex Jupiter analysis
        analysis_request = ChatRequest(
            message=f"Analyze Jupiter DEX integration: {json.dumps(request)}",
            task_type="complex_reasoning",
            preferred_model="claude-3-opus-4",
            context={"integration_type": "jupiter_dex", "priority": "high"}
        )

        response = await chat_with_claudia(analysis_request)
        return response

    except Exception as e:
        logger.error(f"Error in Jupiter analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8890)
