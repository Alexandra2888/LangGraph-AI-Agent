#!/usr/bin/env python3
"""
Test script for image upload functionality
"""

import requests
import base64
import json
from pathlib import Path


def test_image_upload():
    """Test the image upload endpoint"""

    # Test with a local image
    image_path = Path("test_images/dog.jpg")

    if not image_path.exists():
        print(f"❌ Test image not found: {image_path}")
        return False

    try:
        # Test 1: Upload image via file upload endpoint
        print("🧪 Testing image upload endpoint...")

        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/jpeg')}
            response = requests.post(
                'http://localhost:8000/upload-image', files=files)

        if response.status_code == 200:
            print("✅ Image upload endpoint works!")
            image_data = response.json()
            print(f"   - Filename: {image_data['filename']}")
            print(f"   - Type: {image_data['type']}")
            print(f"   - MIME type: {image_data['mime_type']}")
        else:
            print(f"❌ Image upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        # Test 2: Chat with uploaded image
        print("\n🧪 Testing chat with image...")

        chat_request = {
            "message": "What do you see in this image?",
            "images": [image_data]
        }

        response = requests.post(
            'http://localhost:8000/chat',
            headers={'Content-Type': 'application/json'},
            json=chat_request
        )

        if response.status_code == 200:
            print("✅ Chat with image works!")
            chat_response = response.json()
            print(f"   Response: {chat_response['response'][:200]}...")
        else:
            print(f"❌ Chat with image failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        # Test 3: Test streaming with image
        print("\n🧪 Testing streaming chat with image...")

        response = requests.post(
            'http://localhost:8000/chat/stream',
            headers={'Content-Type': 'application/json'},
            json=chat_request,
            stream=True
        )

        if response.status_code == 200:
            print("✅ Streaming chat with image works!")
            print("   Stream events:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])
                            print(
                                f"     - {event_data['event']}: {event_data['data'][:50]}...")
                            if event_data['event'] == 'done':
                                break
                        except json.JSONDecodeError:
                            continue
        else:
            print(
                f"❌ Streaming chat with image failed: {response.status_code}")
            return False

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure to start the server with: python run_server.py")
        return False


if __name__ == "__main__":
    print("🚀 Testing LangGraph Agent Image Upload Functionality\n")

    if test_server_health():
        test_image_upload()
    else:
        print("\n💡 To start the server, run: python run_server.py")
