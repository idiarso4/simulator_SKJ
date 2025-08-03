#!/usr/bin/env python3
"""
Simple HTTP server untuk frontend SKJ Simulator Pro
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_frontend():
    """Start frontend server"""
    print(f"🚀 Starting SKJ Simulator Pro Frontend...")
    print(f"📁 Serving files from: {DIRECTORY}")
    print(f"🌐 Frontend URL: http://localhost:{PORT}")
    print(f"🔗 Backend URL: http://127.0.0.1:5001/api")
    print(f"\n📋 Instructions:")
    print(f"   1. Make sure backend is running on port 5001")
    print(f"   2. Open http://localhost:{PORT} in your browser")
    print(f"   3. Frontend will auto-detect backend")
    print(f"\n⚠️  Press Ctrl+C to stop the server")
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"\n✅ Frontend server started successfully!")
            
            # Auto-open browser
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print(f"🌐 Browser opened automatically")
            except:
                print(f"🌐 Please open http://localhost:{PORT} manually")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n👋 Frontend server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use")
            print(f"💡 Try a different port or stop the existing server")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_frontend()