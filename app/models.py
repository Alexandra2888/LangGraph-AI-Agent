from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union
from datetime import datetime


class ImageData(BaseModel):
    """Model for image data"""
    data: str = Field(...,
                      description="Base64 encoded image data or image URL")
    type: Literal["base64",
                  "url"] = Field(..., description="Type of image data")
    filename: Optional[str] = Field(
        None, description="Original filename if uploaded")
    mime_type: Optional[str] = Field(
        None, description="MIME type of the image")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(...,
                         description="The user's message to the agent", min_length=1)
    session_id: Optional[str] = Field(
        None, description="Optional session ID for conversation tracking")
    images: Optional[List[ImageData]] = Field(
        None, description="Optional list of images to analyze")


class StreamingChatRequest(BaseModel):
    """Request model for streaming chat endpoint"""
    message: str = Field(...,
                         description="The user's message to the agent", min_length=1)
    session_id: Optional[str] = Field(
        None, description="Optional session ID for conversation tracking")
    stream: bool = Field(default=True, description="Enable streaming response")
    images: Optional[List[ImageData]] = Field(
        None, description="Optional list of images to analyze")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="The agent's response")
    session_id: Optional[str] = Field(
        None, description="Session ID if provided")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp")
    status: str = Field(default="success", description="Response status")


class StreamingEvent(BaseModel):
    """Model for streaming events"""
    event: Literal["token", "tool_start", "tool_end", "error", "done"] = Field(
        ..., description="Type of streaming event")
    data: str = Field(..., description="Event data")
    session_id: Optional[str] = Field(None, description="Session ID")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Event timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    status: str = Field(default="error", description="Response status")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(default="healthy", description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Health check timestamp")
    version: str = Field(default="0.1.0", description="API version")


class AgentCapabilities(BaseModel):
    """Model for agent capabilities"""
    name: str
    description: str
    examples: List[str]


class AgentInfoResponse(BaseModel):
    """Response model for agent info endpoint"""
    name: str = Field(default="LangGraph Agent", description="Agent name")
    description: str = Field(
        default="AI assistant with multiple capabilities", description="Agent description")
    capabilities: List[AgentCapabilities] = Field(
        ..., description="List of agent capabilities")
    status: str = Field(default="active", description="Agent status")
