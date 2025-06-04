#!/usr/bin/env python3
"""
Final test script to verify streaming functionality
"""
import requests
import json
import time


def test_streaming_comprehensive():
    """Comprehensive test of streaming functionality"""
    base_url = "http://localhost:8000"

    print("🧪 Comprehensive Streaming Test")
    print("=" * 50)

    # Test messages
    test_messages = [
        "Tell me a joke",
        "Calculate 2 + 2",
        "What can you do?",
        "Search for Python news"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n[Test {i}/{len(test_messages)}] Message: {message}")
        print("-" * 40)

        # Test streaming
        url = f"{base_url}/chat/stream"
        payload = {
            "message": message,
            "stream": True
        }

        try:
            response = requests.post(
                url, json=payload, stream=True, timeout=30)

            if response.status_code == 200:
                print("✅ Streaming Response: ", end="", flush=True)

                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                event_data = json.loads(line_str[6:])

                                if event_data.get('event') == 'token':
                                    token = event_data.get('data', '')
                                    print(token, end="", flush=True)
                                    full_response += token
                                elif event_data.get('event') == 'tool_start':
                                    print(
                                        f"\n[🔧 {event_data.get('data')}] ", end="", flush=True)
                                elif event_data.get('event') == 'tool_end':
                                    print(
                                        f"\n[✅ {event_data.get('data')}] ", end="", flush=True)
                                elif event_data.get('event') == 'done':
                                    print("\n")
                                    break

                            except json.JSONDecodeError:
                                continue

                print(
                    f"📝 Total response length: {len(full_response)} characters")

            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(1)  # Brief pause between tests


def test_ios_compatibility():
    """Test iOS compatibility features"""
    print("\n🍎 iOS Compatibility Test")
    print("=" * 30)

    # Test CORS headers
    base_url = "http://localhost:8000"

    try:
        # Test OPTIONS request
        response = requests.options(f"{base_url}/chat/stream")
        print(f"OPTIONS Status: {response.status_code}")

        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }

        print("CORS Headers:")
        for header, value in cors_headers.items():
            status = "✅" if value else "❌"
            print(f"  {status} {header}: {value}")

        # Test regular chat endpoint (fallback for iOS)
        print("\n📱 Testing fallback endpoint...")
        response = requests.post(f"{base_url}/chat", json={"message": "Hello"})

        if response.status_code == 200:
            print("✅ Fallback endpoint working")
        else:
            print(f"❌ Fallback endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error testing iOS compatibility: {e}")


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            test_streaming_comprehensive()
            test_ios_compatibility()
        else:
            print("❌ Server not responding properly")
    except:
        print("❌ Server is not running. Start it with: python run_server.py")
