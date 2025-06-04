#!/usr/bin/env python3
"""
Test web search streaming
"""
import requests
import json


def test_search_streaming():
    """Test streaming with web search"""
    print("Testing web search streaming...")
    try:
        response = requests.post(
            'http://localhost:8000/chat/stream',
            json={'message': 'Search for Python FastAPI', 'stream': True},
            stream=True,
            timeout=30
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])
                            print(f"Event: {event_data}")
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_search_streaming()
