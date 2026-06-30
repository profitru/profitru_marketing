#!/usr/bin/env python3
"""Serve static files with Content-Type: text/html; charset=utf-8 for .html (fixes local mojibake)."""
import argparse
import http.server
import os
import socketserver


class UTF8RequestHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
    extensions_map[".html"] = "text/html; charset=utf-8"
    extensions_map[".css"] = "text/css; charset=utf-8"
    extensions_map[".js"] = "text/javascript; charset=utf-8"
    extensions_map[".svg"] = "image/svg+xml; charset=utf-8"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", "-p", type=int, default=8080)
    p.add_argument("--bind", "-b", default="127.0.0.1")
    args = p.parse_args()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer((args.bind, args.port), UTF8RequestHandler) as httpd:
        print(f"Serving {os.getcwd()} at http://{args.bind}:{args.port}/")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
