#!/usr/bin/env python3
"""
Server runner for LangGraph Agent API using Granian
"""
import os
import sys
from pathlib import Path


def main():
    """Start the FastAPI server using Granian"""
    try:
        import granian
    except ImportError:
        print("❌ Granian not found. Installing...")
        os.system("pip install 'granian[reload]'")
        import granian

    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"🚀 Starting LangGraph Agent API Server")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"📂 Working Directory: {Path.cwd()}")
    print()

    # Start the server
    try:
        from granian import Granian
        from granian.constants import Interfaces

        app = Granian(
            "app.main:app",
            address=host,
            port=port,
            interface=Interfaces.ASGI,
            reload=reload,
        )

        print("🎯 Server starting... Press Ctrl+C to stop")
        app.serve()

    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try using: python -m granian --interface asgi app.main:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)


if __name__ == "__main__":
    main()
