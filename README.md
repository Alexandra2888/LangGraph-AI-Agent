# LangGraph Agent API

A powerful AI agent built with LangGraph and FastAPI that provides calculator, web search, database query, and image analysis capabilities with **real-time streaming responses**.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key

### Installation

1. **Clone and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Server

**Recommended:**
```bash
python run_server.py
```

**Alternative methods:**
```bash
# Using Granian directly
python -m granian --interface asgi app.main:app --host 0.0.0.0 --port 8000 --reload

# CLI version
python main.py
```

### Testing

```bash
python test_server.py    # Test basic endpoints
python test_tools.py     # Test agent capabilities  
python test_streaming.py # Test streaming functionality
```

**Interactive API docs:** `http://localhost:8000/docs`

## 🛠️ Agent Capabilities

| Tool | Description | Example |
|------|-------------|---------|
| **Calculator** | Mathematical calculations | `"Calculate 15 * 8 + sqrt(144)"` → `132.0` |
| **Web Search** | DuckDuckGo search | `"Search for Python tutorials"` → Top results with links |
| **Database** | User information lookup | `"Fetch user2 from database"` → User details |
| **Image Analysis** | Analyze images from URLs/files | `"Analyze this image: https://..."` |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/health` | Health check |
| `GET` | `/agent/info` | Agent information |
| `GET` | `/agent/capabilities` | Available tools |
| `POST` | `/chat` | Chat with agent (regular) |
| `POST` | `/chat/stream` | **Chat with streaming responses** |

### Regular Chat
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Calculate 25 * 4 + sqrt(81)"}'
```

### Streaming Chat
```bash
curl -X POST "http://localhost:8000/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{"message": "Calculate 25 * 4", "stream": true}' \
     --no-buffer
```

## 🌊 Streaming Features

### Real-time Token Streaming
- **Token-by-token responses** as they're generated
- **Tool execution status** updates in real-time
- **Better user experience** with immediate feedback

### Streaming Events
| Event | Description |
|-------|-------------|
| `token` | Individual response tokens |
| `tool_start` | Tool execution beginning |
| `tool_end` | Tool execution completed |
| `error` | Error handling |
| `done` | Response completion |

### Web Client
Open `streaming_client.html` in your browser for a beautiful real-time chat interface.

### Python Streaming Client
```python
import requests
import json

def stream_chat(message):
    response = requests.post(
        'http://localhost:8000/chat/stream',
        json={"message": message, "stream": True},
        stream=True
    )
    
    for line in response.iter_lines():
        if line and line.startswith(b'data: '):
            event = json.loads(line[6:])
            if event['event'] == 'token':
                print(event['data'], end='', flush=True)

# Usage
stream_chat("What can you do?")
```

## 🏗️ Project Structure

```
langgraph-agent/
├── app/
│   ├── main.py          # FastAPI application with streaming
│   ├── agent.py         # LangGraph agent implementation
│   └── models.py        # Pydantic models
├── test_server.py       # API endpoint tests
├── test_tools.py        # Agent capability tests
├── test_streaming.py    # Streaming functionality tests
├── streaming_client.html # Web client for testing
├── run_server.py        # Server runner script
├── main.py              # CLI version
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🔧 Development

**Start with auto-reload:**
```bash
python -m granian --interface asgi app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Environment variables:**
```env
# Required
OPENAI_API_KEY=your_key_here

# Optional
HOST=0.0.0.0
PORT=8000
RELOAD=true
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0
```

## ✅ Status

All components working correctly:
- ✅ Server starts successfully
- ✅ API endpoints respond
- ✅ **Streaming responses work**
- ✅ Calculator tool works
- ✅ Database tool works  
- ✅ Search tool works
- ✅ Image analysis available
- ✅ Error handling implemented

## 🧪 Testing Streaming

### Interactive Mode
```bash
python test_streaming.py
```

### Batch Testing
```bash
python test_streaming.py batch
```

### Single Message
```bash
python test_streaming.py single "Calculate 2+2"
```

## 🐛 Troubleshooting

**Server won't start:**
- Check if port 8000 is available
- Verify OpenAI API key is set
- Install missing dependencies: `pip install -r requirements.txt`

**Streaming not working:**
- Ensure you're using the `/chat/stream` endpoint
- Check that `stream: true` is in the request body
- Verify the client supports Server-Sent Events

**Tools not working:**
- Ensure OpenAI API key is valid
- Check internet connection for search tool
