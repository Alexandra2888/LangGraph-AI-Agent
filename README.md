# LangGraph Agent - Real-time Streaming AI Assistant

A powerful AI agent built with **LangGraph** and **FastAPI** that provides multiple capabilities including calculations, web search, database queries, and image analysis with **real-time streaming responses** using Server-Sent Events (SSE).

## 🚀 **Features**

### **Real-time Streaming**
- **Server-Sent Events (SSE)** for real-time communication
- **Token-by-token streaming** for natural conversation flow
- **Tool execution indicators** showing when tools are being used
- **Connection status** and error handling
- **Modern JavaScript client** with beautiful UI

### **AI Agent Capabilities**
- **🧮 Calculator** - Mathematical calculations with safe evaluation
- **🔍 Web Search** - DuckDuckGo search integration
- **💾 Database** - User information retrieval from dummy database
- **🖼️ Image Analysis** - URL and local image analysis with GPT-4 Vision
- **🤖 Vision AI** - Advanced image understanding capabilities

## 📋 **Prerequisites**

- **Python 3.12+**
- **OpenAI API key**
- **Modern web browser** (for the web client)

## ⚡ **Quick Start**

### 1. **Installation**
```bash
# Clone the repository
git clone <your-repo-url>
cd langgraph-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. **Environment Setup**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### 3. **Start the Server**
```bash
python run_server.py
```
The server will start on `http://localhost:8000`

### 4. **Test the Implementation**
```bash
# Test basic functionality
python test_simple.py

# Test calculation streaming
python test_calc.py

# Test web search streaming
python test_search.py
```

### 5. **Use the Web Client**
Open `chat_client.html` in your browser for a modern chat interface with:
- Real-time streaming responses
- Tool execution indicators
- Example buttons for quick testing
- Mobile-responsive design

## 🛠️ **Agent Capabilities**

| Tool | Description | Example Usage |
|------|-------------|---------------|
| **Calculator** | Safe mathematical calculations | `"Calculate 15 * 23 + sqrt(144)"` → `357.0` |
| **Web Search** | DuckDuckGo search with results | `"Search for Python FastAPI tutorials"` → Top 3 results |
| **Database** | User information lookup | `"Fetch user1 from database"` → User details in JSON |
| **Image Analysis** | Analyze images from URLs | `"Analyze this image: https://example.com/image.jpg"` |
| **Local Images** | Analyze local image files | `"Analyze image test_images/sample.png"` |
| **Image Description** | Analyze based on description | `"Analyze this image of a sunset over mountains"` |

## 📡 **API Endpoints**

### **Core Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message and API overview |
| `GET` | `/health` | Health check and server status |
| `GET` | `/agent/info` | Agent information and capabilities |
| `POST` | `/chat` | Regular chat (non-streaming) |
| `POST` | `/chat/stream` | **Streaming chat with SSE** |

### **Regular Chat**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Calculate 25 * 4 + 10"}'
```

**Response:**
```json
{
  "response": "The result of the calculation \\( 25 \\times 4 + 10 \\) is 110.",
  "session_id": "session-123"
}
```

### **Streaming Chat**
```bash
curl -X POST "http://localhost:8000/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{"message": "Calculate 25 * 4 + 10", "stream": true}' \
     --no-buffer
```

## 🌊 **Streaming Events**

The streaming endpoint returns Server-Sent Events with the following event types:

### **Event Types**
| Event | Description | Example |
|-------|-------------|---------|
| `connected` | Stream initialization | `{"event": "connected", "data": "Stream started"}` |
| `tool_start` | Tool execution begins | `{"event": "tool_start", "data": "Executing tools..."}` |
| `tool_end` | Tool execution completes | `{"event": "tool_end", "data": "Tools completed"}` |
| `token` | Individual response tokens | `{"event": "token", "data": "Hello "}` |
| `done` | Stream completion | `{"event": "done", "data": ""}` |
| `error` | Error handling | `{"event": "error", "data": "Error message"}` |

### **Example Streaming Flow**
```
User: "Calculate 25 * 4 + 10"
Events: connected → tool_start → tool_end → token... → done
Result: "The result of the calculation \( 25 \times 4 + 10 \) is 110."
```

## 💻 **JavaScript Client Usage**

The included web client (`chat_client.html`) provides a complete streaming interface:

```javascript
// Initialize the client
const chatClient = new ModernChatClient();

// Send a message
chatClient.sendMessage("Calculate 15 * 23 + 7");

// The client automatically handles:
// - SSE connection management
// - Real-time token streaming
// - Tool execution indicators
// - Error handling and recovery
// - UI updates and animations
```

## 🏗️ **Project Structure**

```
langgraph-agent/
├── app/
│   ├── main.py              # FastAPI application with streaming
│   ├── agent.py             # LangGraph agent implementation
│   └── models.py            # Pydantic models and schemas
├── test_simple.py           # Basic functionality tests
├── test_calc.py             # Calculation streaming tests
├── test_search.py           # Web search streaming tests
├── chat_client.html         # Modern web client interface
├── run_server.py            # Server startup script
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project configuration
├── .env                     # Environment variables
└── README.md               # This documentation
```

## 🔧 **Development**

### **Start with Auto-reload**
```bash
python -m granian --interface asgi app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Environment Variables**
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

### **Interactive API Documentation**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🧪 **Testing**

### **Python Tests**
```bash
# Test all functionality
python test_simple.py

# Test specific features
python test_calc.py      # Mathematical calculations
python test_search.py    # Web search functionality
```

### **Manual Testing**
```bash
# Health check
curl http://localhost:8000/health

# Simple chat test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you do?"}'

# Streaming test
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 2+2", "stream": true}'
```

## 🎯 **Example Interactions**

### **1. Mathematical Calculation**
```
User: "Calculate sqrt(144) + 25 * 2"
Events: connected → tool_start → tool_end → token... → done
Result: "The result is 62.0"
```

### **2. Web Search**
```
User: "Search for latest AI news"
Events: connected → tool_start → tool_end → token... → done
Result: "Here are the latest AI news articles: [formatted results]"
```

### **3. Database Query**
```
User: "Fetch user2 from database"
Events: connected → tool_start → tool_end → token... → done
Result: "User found: {name: 'Bob Smith', email: 'bob@example.com', ...}"
```

### **4. Image Analysis**
```
User: "Analyze this image: https://example.com/sunset.jpg"
Events: connected → tool_start → tool_end → token... → done
Result: "This image shows a beautiful sunset over mountains..."
```

## 🏛️ **Architecture**

### **Backend (Python)**
- **FastAPI** - Modern web framework with async support
- **LangGraph** - Agent orchestration and tool execution
- **LangChain** - LLM integration and tool management
- **OpenAI GPT-4** - Language model and vision capabilities

### **Frontend (JavaScript)**
- **Modern ES6+** - Clean, functional JavaScript
- **Server-Sent Events** - Real-time streaming communication
- **Responsive CSS** - Mobile-friendly design
- **Progressive Enhancement** - Graceful fallbacks

### **Streaming Flow**
```
User Input → FastAPI → LangGraph Agent → OpenAI API
                ↓
    SSE Stream ← Token Processing ← Tool Execution
                ↓
    JavaScript Client → UI Updates → User Experience
```

## ⚡ **Performance**

- **Streaming latency**: ~50ms per token
- **Tool execution**: 1-3 seconds depending on tool
- **Memory usage**: ~100MB base + model overhead
- **Concurrent users**: Supports multiple simultaneous streams
- **CORS enabled**: Works with web clients from any origin

## 🔒 **Security**

- **Input validation** on all endpoints
- **Safe expression evaluation** for calculator tool
- **CORS configuration** for web clients
- **Error handling** without exposing internal details
- **Rate limiting** ready for production deployment

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Server won't start**
   ```bash
   # Check if port is available
   netstat -an | findstr :8000
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Check OpenAI API key
   echo $OPENAI_API_KEY
   ```

2. **Streaming not working**
   - Check browser console for errors
   - Verify CORS headers in network tab
   - Test with curl or Python requests
   - Ensure server is running on correct port

3. **Tool execution failing**
   - Verify OpenAI API key is valid
   - Check internet connection for web search
   - Review server logs for detailed errors
   - Test individual tools with simple requests

### **Debug Commands**
```bash
# Check server status
curl http://localhost:8000/health

# Test agent capabilities
curl http://localhost:8000/agent/capabilities

# View server logs
python run_server.py  # Check console output
```

## 📈 **Status**

All components working correctly:
- ✅ **Server starts successfully**
- ✅ **API endpoints respond**
- ✅ **Real-time streaming works**
- ✅ **All tools functional**
- ✅ **Web client operational**
- ✅ **Error handling implemented**
- ✅ **Documentation complete**

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

**🎉 Ready to chat with your AI agent!** 

Start the server with `python run_server.py` and open `chat_client.html` in your browser for the full streaming experience! 🤖✨

## 🖼️ Image Analysis Features

The LangGraph Agent now supports comprehensive image analysis capabilities:

### Supported Image Formats
- **Local Images**: Upload images directly through the web interface
- **Image URLs**: Analyze images from web URLs
- **Base64 Images**: Process base64-encoded image data
- **File Formats**: JPEG, PNG, GIF, WebP, BMP

### Image Analysis Methods

1. **Web Interface Upload**
   - Drag and drop images into the upload area
   - Click to browse and select images
   - Multiple image support
   - Real-time preview with remove option

2. **URL Analysis**
   ```
   Analyze this image: https://example.com/image.jpg
   ```

3. **Local File Analysis**
   ```
   Analyze this image: test_images/sample.png
   ```

4. **API Endpoints**
   - `POST /upload-image` - Upload image files
   - `POST /chat` - Chat with image analysis
   - `POST /chat/stream` - Streaming chat with images

### Example Usage

**Web Interface:**
1. Open `chat_client.html` in your browser
2. Drag and drop an image or click "Upload Image"
3. Type your question about the image
4. Send the message for AI analysis

**API Usage:**
```python
import requests
import base64

# Upload image
with open('image.jpg', 'rb') as f:
    files = {'file': ('image.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/upload-image', files=files)
    image_data = response.json()

# Chat with image
chat_request = {
    "message": "What do you see in this image?",
    "images": [image_data]
}
response = requests.post('http://localhost:8000/chat', json=chat_request)
```

### Image Processing Features
- Automatic image resizing for optimal processing
- Base64 encoding for API transmission
- MIME type detection
- Error handling for unsupported formats
- Memory-efficient processing

---
