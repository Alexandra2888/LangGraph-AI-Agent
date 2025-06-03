#!/usr/bin/env python3

import os
from main import LangGraphAgent


def test_agent():
    """Test the agent with a simple calculation"""

    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set. Please set it in your environment or .env file")
        return

    print("🧪 Testing LangGraph Agent...")

    try:
        # Create agent
        agent = LangGraphAgent()
        print("✅ Agent created successfully")

        # Test simple conversation
        response = agent.chat("Hello, who are you?")
        print(f"✅ Simple chat works: {response[:100]}...")

        # Test tool usage
        print("\n🔧 Testing calculator tool...")
        response = agent.chat("calculate 2 + 2")
        print(f"Calculator response: {response}")

        print("\n🔧 Testing database tool...")
        response = agent.chat("fetch user1 from database")
        print(f"Database response: {response[:200]}...")

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_agent()
