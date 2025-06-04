#!/usr/bin/env python3
"""
Test script for the streaming LangGraph Agent API
"""
import requests
import json
import time
import sys
from typing import Generator


class StreamingChatClient:
    """Client for testing the streaming chat API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"

    def test_regular_chat(self, message: str) -> str:
        """Test the regular (non-streaming) chat endpoint"""
        url = f"{self.base_url}/chat"
        payload = {
            "message": message,
            "session_id": self.session_id
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

    def stream_chat(self, message: str) -> Generator[dict, None, None]:
        """Stream chat responses from the API"""
        url = f"{self.base_url}/chat/stream"
        payload = {
            "message": message,
            "session_id": self.session_id,
            "stream": True
        }

        try:
            with requests.post(url, json=payload, stream=True, timeout=60) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                event_data = json.loads(line_str[6:])
                                yield event_data
                            except json.JSONDecodeError as e:
                                print(f"Error parsing JSON: {e}")
                                continue

        except requests.exceptions.RequestException as e:
            yield {"event": "error", "data": str(e)}

    def test_streaming_interactive(self):
        """Interactive streaming chat test"""
        print("🤖 LangGraph Agent - Streaming Chat Test")
        print("=" * 50)
        print("Type 'quit' to exit, 'help' for examples")
        print()

        while True:
            try:
                message = input("You: ").strip()

                if message.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break

                if message.lower() == 'help':
                    self.show_examples()
                    continue

                if not message:
                    continue

                print("Agent: ", end="", flush=True)

                # Stream the response
                full_response = ""
                for event in self.stream_chat(message):
                    if event["event"] == "token":
                        print(event["data"], end="", flush=True)
                        full_response += event["data"]
                    elif event["event"] == "tool_start":
                        print(f"\n[🔧 {event['data']}]", end="", flush=True)
                    elif event["event"] == "tool_end":
                        print(f"\n[✅ {event['data']}]", end="", flush=True)
                    elif event["event"] == "error":
                        print(f"\n❌ Error: {event['data']}")
                        break
                    elif event["event"] == "done":
                        print("\n")
                        break

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def test_streaming_batch(self, messages: list):
        """Test streaming with a batch of messages"""
        print("🧪 Batch Streaming Test")
        print("=" * 30)

        for i, message in enumerate(messages, 1):
            print(f"\n[Test {i}/{len(messages)}] Message: {message}")
            print("-" * 40)
            print("Response: ", end="", flush=True)

            full_response = ""
            start_time = time.time()

            for event in self.stream_chat(message):
                if event["event"] == "token":
                    print(event["data"], end="", flush=True)
                    full_response += event["data"]
                elif event["event"] == "tool_start":
                    print(f"\n[🔧 {event['data']}] ", end="", flush=True)
                elif event["event"] == "tool_end":
                    print(f"\n[✅ {event['data']}] ", end="", flush=True)
                elif event["event"] == "error":
                    print(f"\n❌ Error: {event['data']}")
                    break
                elif event["event"] == "done":
                    end_time = time.time()
                    print(f"\n⏱️  Response time: {end_time - start_time:.2f}s")
                    print(f"📝 Total characters: {len(full_response)}")
                    break

            print()

    def show_examples(self):
        """Show example messages"""
        examples = [
            "Calculate sqrt(144) + 25",
            "Search for latest Python news",
            "Fetch user1 from database",
            "What can you do?",
            "Tell me a joke",
            "Analyze this image description: a sunset over mountains"
        ]

        print("\n💡 Example messages:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
        print()

    def check_server_health(self) -> bool:
        """Check if the server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


def main():
    """Main test function"""
    client = StreamingChatClient()

    # Check server health
    print("🔍 Checking server health...")
    if not client.check_server_health():
        print("❌ Server is not running or not responding")
        print("💡 Make sure to start the server with: python run_server.py")
        sys.exit(1)

    print("✅ Server is running!")
    print()

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            # Run batch test
            test_messages = [
                "Hello! What can you do?",
                "Calculate 15 * 23 + 7",
                "Search for FastAPI tutorials",
                "Fetch user2 from database"
            ]
            client.test_streaming_batch(test_messages)
        elif sys.argv[1] == "single":
            # Single message test
            message = " ".join(sys.argv[2:]) if len(
                sys.argv) > 2 else "Hello, how are you?"
            print(f"Testing single message: {message}")
            print("Response: ", end="", flush=True)

            for event in client.stream_chat(message):
                if event["event"] == "token":
                    print(event["data"], end="", flush=True)
                elif event["event"] == "done":
                    print("\n")
                    break
        else:
            print("Usage: python test_streaming.py [batch|single|interactive]")
            print("  batch: Run batch test with predefined messages")
            print("  single <message>: Test a single message")
            print("  interactive (default): Interactive chat mode")
    else:
        # Interactive mode (default)
        client.test_streaming_interactive()


if __name__ == "__main__":
    main()
