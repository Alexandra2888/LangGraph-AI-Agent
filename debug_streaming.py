#!/usr/bin/env python3
"""
Debug script for streaming endpoint
"""
import requests
import json
import time


def test_streaming():
    """Test the streaming endpoint"""
    url = "http://localhost:8000/chat/stream"
    payload = {
        "message": "Calculate 2 + 2 * 3",
        "stream": True
    }

    print("Testing streaming endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    print("-" * 50)

    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("-" * 50)

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return

        print("Streaming response:")
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                print(f"Raw line: {repr(line_str)}")

                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        print(f"Parsed event: {event_data}")

                        if event_data.get('event') == 'token':
                            print(
                                f"Token: {event_data.get('data')}", end='', flush=True)
                        elif event_data.get('event') == 'tool_start':
                            print(f"\n🔧 Tool Start: {event_data.get('data')}")
                        elif event_data.get('event') == 'tool_end':
                            print(f"\n✅ Tool End: {event_data.get('data')}")
                        elif event_data.get('event') == 'done':
                            print("\nDone!")
                            break

                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")

    except Exception as e:
        print(f"Error: {e}")


def test_regular_chat():
    """Test regular chat endpoint for comparison"""
    url = "http://localhost:8000/chat"
    payload = {
        "message": "Calculate 2 + 2 * 3"
    }

    print("\nTesting regular chat endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    print("-" * 50)

    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response')}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_regular_chat()
    test_streaming()
