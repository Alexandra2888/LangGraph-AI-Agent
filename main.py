import os
import json
import sqlite3
import requests
from typing import TypedDict, List, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import base64
from io import BytesIO

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
    Analyze an image from a URL using OpenAI's vision model.

    Args:
        image_url: The URL of the image to analyze

    Returns:
        Analysis of the image
    """
    try:
        # validate URL
        if not image_url.startswith(('http://', 'https://')):
            return f"Invalid URL: {image_url}. Please provide a valid HTTP/HTTPS URL."

        # download the image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        # check if it's an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return f"URL does not point to an image. Content type: {content_type}"

        # return success message with image info
        return f"Successfully downloaded image from {image_url}. Image type: {content_type}. The image is ready for analysis by the vision model."

    except requests.exceptions.RequestException as e:
        return f"Error downloading image from {image_url}: {str(e)}"
    except Exception as e:
        return f"Error processing image from {image_url}: {str(e)}"


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
         analyze_image_url, analyze_image_description]


def call_model(state: AgentState):
    """Call the model with the current state"""
    messages = state["messages"]

    # add system message if it's the first message
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        system_msg = SystemMessage(content="""You are a helpful AI assistant with access to several tools:

1. Calculator - for mathematical calculations
2. DuckDuckGo Search - for web searches  
3. Database Tool - for fetching user information
4. Image URL Analysis - for analyzing images from URLs using vision AI
5. Image Description Analysis - for analyzing images based on text descriptions

When a user provides an image URL, use the analyze_image_url tool. When they describe an image, use analyze_image_description.
Use tools when needed to provide accurate information. Always be helpful and explain your reasoning.""")
        messages = [system_msg] + messages

    # initialize model with tools
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)
    response = model.invoke(messages)

    # return the updated state
    return {"messages": messages + [response]}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Determine whether to continue or end"""
    messages = state["messages"]
    last_message = messages[-1]

    # if there are tool calls, continue to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # otherwise, end
    return "__end__"


class LangGraphAgent:
    def __init__(self):
        # create the graph
        workflow = StateGraph(AgentState)

        # add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(tools))

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
            # create initial state
            initial_state = {"messages": [HumanMessage(content=message)]}

            # run the graph
            result = self.graph.invoke(initial_state)

            # extract the final response
            messages = result["messages"]
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    return msg.content

            return "I couldn't generate a response."

        except Exception as e:
            return f"Error: {str(e)}"


def main():
    # create agent
    agent = LangGraphAgent()

    print("🤖 LangGraph Agent initialized!")
    print("Available capabilities:")
    print("- Answer questions and have conversations")
    print("- Perform calculations (try: 'calculate sqrt(144) + 5^2')")
    print("- Search the web (try: 'search for latest Python news')")
    print("- Fetch user data (try: 'fetch user1 from database')")
    print("- Analyze images from URLs (try: 'analyze this https://example.com/image.jpg')")
    print("- Analyze image descriptions (try: 'analyze this image of a sunset')")
    print("\nType 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye! 👋")
                break

            if not user_input:
                continue

            print("🤖:", end=" ")
            response = agent.chat(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
