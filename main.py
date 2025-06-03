import os
import json
import sqlite3
from typing import TypedDict, List, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from duckduckgo_search import DDGS
from dotenv import load_dotenv

# Load environment variables
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
def analyze_image(image_description: str) -> str:
    """
    Analyze an image description (placeholder for actual image processing).

    Args:
        image_description: Description of the image to analyze

    Returns:
        Analysis of the image
    """
    return f"Image analysis for '{image_description}': This appears to be a {image_description.lower()}. I can see various visual elements that suggest specific characteristics of this type of image."


# create tool list and mapping
tools = [calculator, duckduckgo_search,
         fetch_user_from_database, analyze_image]
tools_by_name = {tool.name: tool for tool in tools}


def call_model(state: AgentState):
    """Call the model with the current state"""
    messages = state["messages"]

    # add system message if it's the first message or if no system message exists
    has_system_message = any(isinstance(msg, SystemMessage)
                             for msg in messages)
    if not has_system_message:
        system_msg = SystemMessage(content="""You are a helpful AI assistant with access to several tools:

1. Calculator - for mathematical calculations
2. DuckDuckGo Search - for web searches  
3. Database Tool - for fetching user information
4. Image Analysis - for analyzing images

Use tools when needed to provide accurate information. Always be helpful and explain your reasoning.""")
        messages = [system_msg] + messages

    # initialize model with tools
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)
    response = model.invoke(messages)

    # return the updated state
    return {"messages": messages + [response]}


def execute_tools(state: AgentState):
    """Execute tools based on the last AI message"""
    messages = state["messages"]
    last_message = messages[-1]

    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": messages}

    new_messages = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]

        if tool_name in tools_by_name:
            try:
                # execute the tool
                tool_result = tools_by_name[tool_name].invoke(tool_args)

                # create tool message
                tool_message = ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call_id
                )
                new_messages.append(tool_message)

            except Exception as e:
                # create error tool message
                tool_message = ToolMessage(
                    content=f"Error executing {tool_name}: {str(e)}",
                    tool_call_id=tool_call_id
                )
                new_messages.append(tool_message)
        else:
            # unknown tool
            tool_message = ToolMessage(
                content=f"Unknown tool: {tool_name}",
                tool_call_id=tool_call_id
            )
            new_messages.append(tool_message)

    return {"messages": messages + new_messages}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Determine whether to continue or end"""
    messages = state["messages"]
    last_message = messages[-1]

    # if there are tool calls, continue to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # Otherwise, end
    return "__end__"


class LangGraphAgent:
    def __init__(self):
        # create the graph
        workflow = StateGraph(AgentState)

        # add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", execute_tools)

        # set entry point
        workflow.set_entry_point("agent")

        # add edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "__end__": END
            }
        )
        workflow.add_edge("tools", "agent")

        # compile the graph
        self.graph = workflow.compile()

        # initialize conversation state
        self.conversation_state = {"messages": []}

    def chat(self, message: str) -> str:
        """Chat with the agent"""
        try:
            # add the new human message to the conversation state
            self.conversation_state["messages"].append(
                HumanMessage(content=message))

            # run the graph with the current conversation state
            result = self.graph.invoke(self.conversation_state)

            # update the conversation state with the result
            self.conversation_state = result

            # extract the final response
            messages = result["messages"]
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    # check if this is a final response (no tool calls or empty tool calls)
                    if not hasattr(msg, 'tool_calls') or not msg.tool_calls:
                        return msg.content

            return "I couldn't generate a response."

        except Exception as e:
            return f"Error: {str(e)}"

    def reset_conversation(self):
        """Reset the conversation state"""
        self.conversation_state = {"messages": []}


def main():
    # create agent
    agent = LangGraphAgent()

    print("🤖 LangGraph Agent initialized!")
    print("Available capabilities:")
    print("- Answer questions and have conversations")
    print("- Perform calculations (try: 'calculate sqrt(144) + 5^2')")
    print("- Search the web (try: 'search for latest Python news')")
    print("- Fetch user data (try: 'fetch user1 from database')")
    print("- Analyze images (try: 'analyze this image of a sunset')")
    print("\nCommands:")
    print("- Type 'reset' to clear conversation history")
    print("- Type 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye! 👋")
                break

            if user_input.lower() == 'reset':
                agent.reset_conversation()
                print("🔄 Conversation history cleared!")
                continue

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
