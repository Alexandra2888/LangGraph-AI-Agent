# LangGraph Agent API

A powerful AI agent built with LangGraph and FastAPI that provides calculator, web search, database query, and image analysis capabilities.

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

**Option 1: Using run_server.py (Recommended)**
```bash
python run_server.py
```

**Option 2: Using Granian directly**
```bash
python -m granian --interface asgi app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: CLI version**
```bash
python main.py
```

### Testing

**Test the API:**
```bash
python test_server.py    # Test basic endpoints
python test_tools.py     # Test agent capabilities
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
| `POST` | `/chat` | Chat with agent |

### Example API Usage

```bash
# Chat with the agent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Calculate 25 * 4 + sqrt(81)"}'

# Response: {"response": "The result is 109.0"}
```

## 🏗️ Project Structure

```
langgraph-agent/
├── app/
│   ├── main.py          # FastAPI application
│   ├── agent.py         # LangGraph agent implementation
│   └── models.py        # Pydantic models
├── test_server.py       # API endpoint tests
├── test_tools.py        # Agent capability tests
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
- ✅ Calculator tool works
- ✅ Database tool works  
- ✅ Search tool works
- ✅ Image analysis available
- ✅ Error handling implemented

## 🐛 Troubleshooting

**Server won't start:**
- Check if port 8000 is available
- Verify OpenAI API key is set
- Install missing dependencies: `pip install -r requirements.txt`

**Tools not working:**
- Ensure OpenAI API key is valid
- Check internet connection for search tool

**Import errors:**
- Make sure you're in the project directory
- Activate virtual environment if using one
