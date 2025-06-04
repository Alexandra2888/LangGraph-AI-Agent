import os
import json
import sqlite3
from typing import TypedDict, List, Literal, AsyncGenerator, Generator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path
import asyncio

# load environment variables
load_dotenv()


class AgentState(TypedDict):
    """State of our agent containing messages"""
    messages: List[BaseMessage]


# define tools
@tool
def calculator(expression: str) -> str:
    """
    Calculate mathematical expressions safely.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)", "sin(pi/2)")

    Returns:
        The result of the calculation
    """
    try:
        import math

        # create a safe namespace for evaluation
        safe_dict = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "exp": math.exp,
            "pi": math.pi, "e": math.e,
        }

        result = eval(expression, safe_dict)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool
def duckduckgo_search(query: str, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 3)

    Returns:
        Search results as formatted text
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"No results found for query: {query}"

        formatted_results = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result['title']}\n"
            formatted_results += f"   {result['href']}\n"
            formatted_results += f"   {result['body'][:200]}...\n\n"

        return formatted_results
    except Exception as e:
        return f"Error searching for '{query}': {str(e)}"


@tool
def fetch_user_from_database(user_id: str) -> str:
    """
    Fetch user information from a dummy database.

    Args:
        user_id: The ID of the user to fetch

    Returns:
        User information as JSON string
    """
    try:
        # create dummy database in memory
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        # create and populate dummy users table
        cursor.execute('''
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                age INTEGER,
                city TEXT
            )
        ''')

        dummy_users = [
            ('user1', 'Alice Johnson', 'alice@example.com', 28, 'New York'),
            ('user2', 'Bob Smith', 'bob@example.com', 35, 'San Francisco'),
            ('user3', 'Carol Davis', 'carol@example.com', 42, 'Chicago'),
            ('user4', 'David Wilson', 'david@example.com', 31, 'Austin'),
        ]

        cursor.executemany(
            'INSERT INTO users VALUES (?, ?, ?, ?, ?)', dummy_users)
        conn.commit()

        # fetch the requested user
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_data = {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'age': user[3],
                'city': user[4]
            }
            return f"User found: {json.dumps(user_data, indent=2)}"
        else:
            return f"User with ID '{user_id}' not found. Available IDs: user1, user2, user3, user4"

    except Exception as e:
        return f"Error fetching user '{user_id}': {str(e)}"


@tool
def analyze_image_url(image_url: str) -> str:
    """
    Prepare an image from a URL for analysis.

    Args:
        image_url: The URL of the image to analyze

    Returns:
        Confirmation that the image URL is ready for analysis
    """
    try:
        # validate URL
        if not image_url.startswith(('http://', 'https://')):
            return f"Invalid URL: {image_url}. Please provide a valid HTTP/HTTPS URL."

        return f"IMAGE_URL_READY:{image_url}"

    except Exception as e:
        return f"Error preparing image from {image_url}: {str(e)}"


@tool
def analyze_local_image(file_path: str) -> str:
    """
    Prepare a local image file for analysis by converting it to base64.

    Args:
        file_path: Path to the local image file (relative to current directory or absolute)

    Returns:
        Confirmation that the local image is ready for analysis
    """
    try:
        # convert to Path object for easier handling
        path = Path(file_path)

        # check if file exists
        if not path.exists():
            # try relative to current working directory
            path = Path.cwd() / file_path
            if not path.exists():
                return f"Image file not found: {file_path}. Please check the path."

        # check if it's a file
        if not path.is_file():
            return f"Path is not a file: {file_path}"

        # validate image extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        if path.suffix.lower() not in valid_extensions:
            return f"Unsupported image format: {path.suffix}. Supported formats: {', '.join(valid_extensions)}"

        # open and potentially resize the image
        with Image.open(path) as img:
            # convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # resize if image is too large (to keep base64 size manageable)
            max_size = (1024, 1024)  # max 1024x1024 pixels
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # save to bytes
            img_bytes = BytesIO()

            # determine format for saving
            save_format = 'JPEG'
            if path.suffix.lower() in ['.png', '.gif', '.webp']:
                save_format = 'PNG'

            img.save(img_bytes, format=save_format, quality=85, optimize=True)
            img_bytes.seek(0)

            # encode to base64
            base64_string = base64.b64encode(
                img_bytes.getvalue()).decode('utf-8')

        # detect image format
        image_format = save_format.lower()

        # create data URL
        mime_type = f"image/{image_format}"
        data_url = f"data:{mime_type};base64,{base64_string}"

        return f"LOCAL_IMAGE_READY:{data_url}|{path.name}"

    except Exception as e:
        return f"Error preparing local image '{file_path}': {str(e)}"


@tool
def analyze_image_description(image_description: str) -> str:
    """
    Analyze an image based on a text description (placeholder for when no actual image is available).

    Args:
        image_description: Description of the image to analyze

    Returns:
        Analysis based on the description
    """
    return f"Based on the description '{image_description}': This appears to be a {image_description.lower()}. Without seeing the actual image, I can provide general insights about this type of visual content and suggest what elements might typically be present."


# create tool list
tools = [calculator, duckduckgo_search, fetch_user_from_database,
         analyze_image_url, analyze_local_image, analyze_image_description]


def call_model(state: AgentState):
    """Call the model with the current state"""
    messages = state["messages"]

    # Add system message if it's the first message
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        system_msg = SystemMessage(content="""You are a helpful AI assistant with access to several tools:

1. Calculator - for mathematical calculations
2. DuckDuckGo Search - for web searches  
3. Database Tool - for fetching user information
4. Image URL Analysis - for analyzing images from URLs using vision AI
5. Local Image Analysis - for analyzing local image files by path
6. Image Description Analysis - for analyzing images based on text descriptions

When a user provides an image URL, use the analyze_image_url tool. 
When they provide a file path to a local image, use analyze_local_image tool.
When they describe an image, use analyze_image_description.

Use tools when needed to provide accurate information. Always be helpful and explain your reasoning.""")
        messages = [system_msg] + messages

    # check if any tool results contain image data that needs vision analysis
    vision_content = None
    vision_context = ""

    for i, msg in enumerate(reversed(messages)):
        if hasattr(msg, 'content') and isinstance(msg.content, str):
            if msg.content.startswith("IMAGE_URL_READY:"):
                image_url = msg.content.replace("IMAGE_URL_READY:", "")
                vision_content = [
                    {"type": "text", "text": "Please analyze this image and describe what you see in detail."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
                vision_context = f"Image from URL: {image_url}"
                break
            elif msg.content.startswith("LOCAL_IMAGE_READY:"):
                parts = msg.content.replace(
                    "LOCAL_IMAGE_READY:", "").split("|")
                data_url = parts[0]
                filename = parts[1] if len(parts) > 1 else "unknown"
                vision_content = [
                    {"type": "text",
                        "text": f"Please analyze this local image ({filename}) and describe what you see in detail. Include information about objects, people, colors, composition, and any text visible in the image."},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
                vision_context = f"Local image: {filename}"
                break

    # If we have vision content, use vision model
    if vision_content:
        try:
            vision_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            vision_message = HumanMessage(content=vision_content)
            vision_response = vision_model.invoke([vision_message])

            # Create a response message with the vision analysis
            analysis_response = AIMessage(
                content=f"Image analysis for {vision_context}:\n\n{vision_response.content}")
            return {"messages": messages + [analysis_response]}
        except Exception as e:
            error_response = AIMessage(
                content=f"Error analyzing image: {str(e)}")
            return {"messages": messages + [error_response]}

    # use normal model with tools
    try:
        model = ChatOpenAI(model="gpt-4o-mini",
                           temperature=0).bind_tools(tools)
        response = model.invoke(messages)
        return {"messages": messages + [response]}
    except Exception as e:
        # if there's an error with tool messages, try with just the last user message
        print(f"Tool error: {e}")
        user_messages = [msg for msg in messages if isinstance(
            msg, (HumanMessage, SystemMessage))]
        if user_messages:
            try:
                model = ChatOpenAI(model="gpt-4o-mini",
                                   temperature=0).bind_tools(tools)
                # system + last user message
                response = model.invoke(user_messages[-2:])
                return {"messages": messages + [response]}
            except Exception as e2:
                print(f"Fallback error: {e2}")
                # final fallback - no tools
                model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                response = model.invoke([user_messages[-1]])
                return {"messages": messages + [response]}
        else:
            error_response = AIMessage(content=f"Error: {str(e)}")
            return {"messages": messages + [error_response]}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Determine whether to continue or end"""
    messages = state["messages"]
    last_message = messages[-1]

    # if there are tool calls, continue to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # otherwise, end
    return "__end__"


def execute_tools(state: AgentState):
    """Execute tools based on the last message's tool calls"""
    messages = state["messages"]
    last_message = messages[-1]

    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": messages}

    # create a mapping of tool names to functions
    tool_map = {
        "calculator": calculator,
        "duckduckgo_search": duckduckgo_search,
        "fetch_user_from_database": fetch_user_from_database,
        "analyze_image_url": analyze_image_url,
        "analyze_local_image": analyze_local_image,
        "analyze_image_description": analyze_image_description,
    }

    # execute each tool call
    tool_responses = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        if tool_name in tool_map:
            try:
                # execute the tool
                result = tool_map[tool_name].invoke(tool_args)

                # create a tool message with proper structure
                from langchain_core.messages import ToolMessage
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                )
                tool_responses.append(tool_message)

            except Exception as e:
                # create error tool message
                from langchain_core.messages import ToolMessage
                error_message = ToolMessage(
                    content=f"Error executing {tool_name}: {str(e)}",
                    tool_call_id=tool_id
                )
                tool_responses.append(error_message)

    return {"messages": messages + tool_responses}


class LangGraphAgent:
    """LangGraph Agent class for handling conversations"""

    def __init__(self):
        # create the graph
        workflow = StateGraph(AgentState)

        # add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", execute_tools)

        # set entry point
        workflow.set_entry_point("agent")

        # add edges
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")

        # compile the graph
        self.graph = workflow.compile()

    def chat(self, message: str) -> str:
        """Chat with the agent"""
        try:
            # Create initial state
            initial_state = {"messages": [HumanMessage(content=message)]}

            # Run the graph
            result = self.graph.invoke(initial_state)

            # Extract the final response
            messages = result["messages"]
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    return msg.content

            return "I couldn't generate a response."

        except Exception as e:
            return f"Error: {str(e)}"

    def chat_stream(self, message: str) -> Generator[dict, None, None]:
        """Chat with the agent with streaming support"""
        try:
            # Create initial state
            initial_state = {"messages": [HumanMessage(content=message)]}

            # Track tool execution phase and final response
            tool_phase = False
            final_response_sent = False

            # Run the streaming graph
            for event in self.graph.stream(initial_state):
                # Check if we're entering or exiting tool phase
                if "tools" in event:
                    if not tool_phase:
                        yield {"event": "tool_start", "data": "Executing tools..."}
                        tool_phase = True
                elif tool_phase and "agent" in event:
                    yield {"event": "tool_end", "data": "Tools completed"}
                    tool_phase = False

                # Process agent responses
                if "agent" in event:
                    messages = event["agent"]["messages"]
                    last_message = messages[-1] if messages else None

                    if isinstance(last_message, AIMessage) and last_message.content:
                        # Check if this is a final response (no tool calls)
                        has_tool_calls = hasattr(
                            last_message, 'tool_calls') and last_message.tool_calls

                        if not has_tool_calls and not final_response_sent:
                            # This is the final response, stream it token by token
                            content = last_message.content
                            # Stream word by word for better UX
                            words = content.split()
                            for i, word in enumerate(words):
                                token = word + \
                                    (" " if i < len(words) - 1 else "")
                                yield {"event": "token", "data": token}
                            final_response_sent = True

            # Signal completion
            yield {"event": "done", "data": ""}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    async def chat_stream_async(self, message: str) -> AsyncGenerator[dict, None]:
        """Async version of chat_stream with real-time streaming"""
        try:
            # Send connection event
            yield {"event": "connected", "data": "Stream started"}

            # Use asyncio to run the synchronous streaming in a thread
            loop = asyncio.get_event_loop()

            def collect_events():
                """Collect all streaming events"""
                events = []
                try:
                    for event in self.chat_stream(message):
                        events.append(event)
                except Exception as e:
                    events.append({"event": "error", "data": str(e)})
                return events

            # Run in thread pool executor
            events = await loop.run_in_executor(None, collect_events)

            # Yield events with delays for streaming effect
            for event in events:
                yield event
                # Add delay based on event type for better UX
                if event.get("event") == "token":
                    await asyncio.sleep(0.03)  # Faster for tokens
                else:
                    await asyncio.sleep(0.1)   # Slower for other events

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    def get_capabilities(self):
        """Get agent capabilities for API documentation"""
        return [
            {
                "name": "Calculator",
                "description": "Perform mathematical calculations",
                "examples": ["calculate sqrt(144) + 5^2", "what is 2 + 2 * 3?"]
            },
            {
                "name": "Web Search",
                "description": "Search the web using DuckDuckGo",
                "examples": ["search for latest Python news", "find information about FastAPI"]
            },
            {
                "name": "Database Query",
                "description": "Fetch user information from database",
                "examples": ["fetch user1 from database", "get user info for user2"]
            },
            {
                "name": "Image Analysis (URL)",
                "description": "Analyze images from URLs",
                "examples": ["analyze this image https://example.com/image.jpg"]
            },
            {
                "name": "Image Analysis (Local)",
                "description": "Analyze local image files",
                "examples": ["analyze image test_images/sample.png"]
            },
            {
                "name": "Image Description Analysis",
                "description": "Analyze images based on text descriptions",
                "examples": ["analyze this image of a sunset over mountains"]
            }
        ]
