from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List
import uuid

from .models import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
    AgentInfoResponse,
    AgentCapabilities
)
from .agent import LangGraphAgent

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# global agent instance
agent_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global agent_instance

    # startup
    logger.info("🚀 Starting LangGraph Agent API...")
    try:
        agent_instance = LangGraphAgent()
        logger.info("✅ Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        raise

    yield

    # shutdown
    logger.info("🛑 Shutting down LangGraph Agent API...")

# create FastAPI app
app = FastAPI(
    title="LangGraph Agent API",
    description="A powerful AI agent with multiple capabilities including calculations, web search, database queries, and image analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# exception handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=str(exc.detail)).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error="Internal server error").model_dump()
    )

# routes


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LangGraph Agent API",
        "docs": "/docs",
        "health": "/health",
        "agent_info": "/agent/info"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global agent_instance

    if agent_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    return HealthResponse()


@app.get("/agent/info", response_model=AgentInfoResponse)
async def get_agent_info():
    """Get agent information and capabilities"""
    global agent_instance

    if agent_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    capabilities_data = agent_instance.get_capabilities()
    capabilities = [
        AgentCapabilities(
            name=cap["name"],
            description=cap["description"],
            examples=cap["examples"]
        )
        for cap in capabilities_data
    ]

    return AgentInfoResponse(capabilities=capabilities)


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the LangGraph agent"""
    global agent_instance

    if agent_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    try:
        # generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        logger.info(
            f"Processing chat request - Session: {session_id}, Message: {request.message[:100]}...")

        # get response from agent
        response = agent_instance.chat(request.message)

        logger.info(f"Agent response generated - Session: {session_id}")

        return ChatResponse(
            response=response,
            session_id=session_id
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

# additional utility endpoints


@app.get("/agent/capabilities", response_model=List[AgentCapabilities])
async def get_agent_capabilities():
    """Get detailed agent capabilities"""
    global agent_instance

    if agent_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    capabilities_data = agent_instance.get_capabilities()
    return [
        AgentCapabilities(
            name=cap["name"],
            description=cap["description"],
            examples=cap["examples"]
        )
        for cap in capabilities_data
    ]


@app.get("/agent/status")
async def get_agent_status():
    """Get current agent status"""
    global agent_instance

    return {
        "initialized": agent_instance is not None,
        "status": "ready" if agent_instance is not None else "not_initialized"
    }

if __name__ == "__main__":
    from granian import Granian
    from granian.constants import Interfaces

    server = Granian(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        reload=True,
        log_level="info"
    )
    server.serve()
