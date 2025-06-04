# LangGraph Agent - Streaming Implementation

## Overview

This project implements a **real-time streaming chat interface** using Server-Sent Events (SSE) with a LangGraph agent that has multiple capabilities including calculations, web search, database queries, and image analysis.

## Features

### 🚀 **Real-time Streaming**
- **Server-Sent Events (SSE)** for real-time communication
- **Token-by-token streaming** for natural conversation flow
- **Tool execution indicators** showing when tools are being used
- **Connection status** and error handling

### 🛠️ **Agent Capabilities**
- **Calculator** - Mathematical calculations
- **Web Search** - DuckDuckGo search integration
- **Database** - User information retrieval
- **Image Analysis** - URL and local image analysis
- **Vision AI** - GPT-4 Vision for image understanding

## Quick Start

### 1. Start the Server
```bash
python run_server.py
```
The server will start on `http://localhost:8000`

### 2. Test Streaming (Python)
```bash
# Test basic streaming
python test_simple.py

# Test calculation streaming
python test_calc.py
```

### 3. Use the Web Client
Open `chat_client.html` in your browser for a modern chat interface with:
- Real-time streaming responses
- Tool execution indicators
- Example buttons for quick testing
- Mobile-responsive design

## API Endpoints

### Regular Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Calculate 15 * 23 + 7",
  "session_id": "optional-session-id"
}
```

### Streaming Chat
```http
POST /chat/stream
Content-Type: application/json

{
  "message": "Calculate 15 * 23 + 7",
  "session_id": "optional-session-id",
  "stream": true
}
```

## Streaming Events

The streaming endpoint returns Server-Sent Events with the following event types:

### `connected`
```json
{
  "event": "connected",
  "data": "Stream started",
  "session_id": "session-123"
}
```

### `tool_start`
```json
{
  "event": "tool_start", 
  "data": "Executing tools...",
  "session_id": "session-123"
}
```

### `tool_end`
```json
{
  "event": "tool_end",
  "data": "Tools completed", 
  "session_id": "session-123"
}
```

### `token`
```json
{
  "event": "token",
  "data": "Hello ",
  "session_id": "session-123"
}
```

### `done`
```json
{
  "event": "done",
  "data": "",
  "session_id": "session-123"
}
```

### `error`
```json
{
  "event": "error",
  "data": "Error message",
  "session_id": "session-123"
}
```

## JavaScript Client Usage

```javascript
// Initialize the client
const chatClient = new ModernChatClient();

// Send a message
chatClient.sendMessage("Calculate 15 * 23 + 7");

// The client automatically handles:
// - SSE connection management
// - Real-time token streaming
// - Tool execution indicators
// - Error handling
// - UI updates
```

## Example Interactions

### 1. **Mathematical Calculation**
```
User: Calculate 25 * 4 + 10
Events: connected → tool_start → tool_end → token... → done
Result: "The result of the calculation \( 25 \times 4 + 10 \) is 110."
```

### 2. **Web Search**
```
User: Search for latest AI news
Events: connected → tool_start → tool_end → token... → done
Result: Search results with titles, URLs, and descriptions
```

### 3. **Database Query**
```
User: Fetch user1 from database
Events: connected → tool_start → tool_end → token... → done
Result: User information in JSON format
```

## Architecture

### Backend (Python)
- **FastAPI** - Web framework with async support
- **LangGraph** - Agent orchestration and tool execution
- **LangChain** - LLM integration and tool management
- **OpenAI GPT-4** - Language model and vision capabilities

### Frontend (JavaScript)
- **Modern ES6+** - Clean, functional JavaScript
- **Server-Sent Events** - Real-time streaming
- **Responsive CSS** - Mobile-friendly design
- **Progressive Enhancement** - Fallback for older browsers

### Streaming Flow
```
User Input → FastAPI → LangGraph Agent → OpenAI API
                ↓
    SSE Stream ← Token Processing ← Tool Execution
                ↓
    JavaScript Client → UI Updates → User Experience
```

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your-openai-api-key
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### Server Settings
- **Host**: `0.0.0.0` (configurable)
- **Port**: `8000` (configurable)
- **CORS**: Enabled for all origins
- **Streaming**: SSE with proper headers

## Troubleshooting

### Common Issues

1. **Server not starting**
   ```bash
   # Check if port is available
   netstat -an | findstr :8000
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Streaming not working**
   - Check browser console for errors
   - Verify CORS headers
   - Test with `curl` or Python requests

3. **Tool execution failing**
   - Check OpenAI API key
   - Verify internet connection for web search
   - Check server logs for detailed errors

### Testing Commands
```bash
# Health check
curl http://localhost:8000/health

# Test regular chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test streaming
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 2+2", "stream": true}'
```

## Performance

- **Streaming latency**: ~50ms per token
- **Tool execution**: 1-3 seconds depending on tool
- **Memory usage**: ~100MB base + model overhead
- **Concurrent users**: Supports multiple simultaneous streams

## Security

- **Input validation** on all endpoints
- **Safe expression evaluation** for calculator
- **CORS configuration** for web clients
- **Error handling** without exposing internals

---

**Ready to chat with your AI agent!** 🤖✨ 