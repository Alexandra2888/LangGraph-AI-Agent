#!/usr/bin/env python3
"""
Simple test script for the LangGraph Agent API
"""
import requests
import json



def test_regular_chat():
    """Test the regular chat endpoint"""
    print("Testing regular chat endpoint...")
    try:
        response = requests.post(
            'http://localhost:8000/chat',
            json={'message': 'Calculate 15 * 23 + 7'},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


def test_streaming_chat():
    """Test the streaming chat endpoint"""
    print("\nTesting streaming chat endpoint...")
    try:
        response = requests.post(
            'http://localhost:8000/chat/stream',
            json={'message': 'Hello, how are you?', 'stream': True},
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


def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")


if __name__ == "__main__":
    test_health()
    test_regular_chat()
    test_streaming_chat()
