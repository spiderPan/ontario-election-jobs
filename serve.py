#!/usr/bin/env python3
"""
Clean, resilient local HTTP server that suppresses benign browser disconnect / ConnectionReset errors.
"""
import sys
import http.server
import socketserver
import os

PORT = 8000

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Print cleaner logs
        if "404" in str(args) or "500" in str(args):
            sys.stderr.write(f"[HTTP {args[1]}] {args[0]}\n")
        else:
            sys.stdout.write(f"[HTTP {args[1]}] {args[0]}\n")

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError):
            # Suppress benign browser disconnect / page refresh resets
            pass

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PORT
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        print(f"============================================================")
        print(f"  Ontario Election 2026 Dashboard Server Running! ")
        print(f"  URL: http://localhost:{port}")
        print(f"  Analytics: http://localhost:{port}/analytics.html")
        print(f"  (Press Ctrl+C to stop)")
        print(f"============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully...")

if __name__ == "__main__":
    main()
