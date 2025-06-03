#!/usr/bin/env python3
"""
Test script to verify LangGraph Agent tools functionality
"""
import requests
import time


def test_tools():
    """Test the agent's tools functionality"""
    base_url = "http://localhost:8000"

    print("🧪 Testing LangGraph Agent Tools")
    print("=" * 50)

    # Test calculator
    print("🧮 Testing calculator tool...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={"message": "Calculate 15 * 8 + sqrt(144)"},
            timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Calculator working!")
            print(f"Response: {result.get('response', 'No response')}")
        else:
            print(
                f"❌ Calculator test failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Calculator test failed: {e}")

    print("\n" + "="*50)

    # Test database
    print("🗄️ Testing database tool...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={"message": "Fetch user2 from the database"},
            timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Database working!")
            print(f"Response: {result.get('response', 'No response')}")
        else:
            print(f"❌ Database test failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Database test failed: {e}")

    print("\n" + "="*50)

    # Test search (this might take longer)
    print("🔍 Testing search tool...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={"message": "Search for Python programming tutorials"},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Search working!")
            print(
                f"Response: {result.get('response', 'No response')[:200]}...")
        else:
            print(f"❌ Search test failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Search test failed: {e}")


if __name__ == "__main__":
    test_tools()
