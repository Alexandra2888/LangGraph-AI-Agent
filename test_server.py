#!/usr/bin/env python3
"""
Simple test script to check if the LangGraph Agent API server is running
"""
import requests
import time


def test_server():
    """Test if the server is running"""
    base_url = "http://localhost:8000"

    print("🧪 Testing LangGraph Agent API Server")
    print("=" * 50)

    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)

    try:
        # Test root endpoint
        print("🧪 Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")

    try:
        # Test health endpoint
        print("\n🧪 Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"Response: {response.json()}")
        else:
            print(
                f"❌ Health endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")

    try:
        # Test simple chat
        print("\n🧪 Testing simple chat...")
        response = requests.post(
            f"{base_url}/chat",
            json={"message": "Hello, can you help me?"},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Chat endpoint working!")
            result = response.json()
            print(f"Response: {result.get('response', 'No response field')}")
        else:
            print(f"❌ Chat endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")


if __name__ == "__main__":
    test_server()
