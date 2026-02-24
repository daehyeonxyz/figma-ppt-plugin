#!/usr/bin/env python3
"""
serve-and-capture.py — figma-ppt Local Server Helper

Starts a local HTTP server for the slide-output directory,
then prints the ordered list of slide URLs for Claude to call
generate_figma_design on one by one.

This script is run by Claude Code's Bash tool.
The actual generate_figma_design MCP calls are made by Claude itself
after reading the URL list from this script's output.

Usage:
  python serve-and-capture.py \
    --output-dir ./slide-output \
    --port 7890

Output (stdout):
  JSON with server info + ordered slide URL list
  Claude reads this and calls generate_figma_design for each URL.
"""

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


def port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def find_free_port(start=7890):
    """Find a free port starting from `start`."""
    for port in range(start, start + 20):
        if not port_in_use(port):
            return port
    return None


def kill_port(port):
    """Kill whatever is using the given port (cross-platform)."""
    if sys.platform == "win32":
        # Windows
        os.system(f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{port}') do taskkill /F /PID %a >nul 2>&1")
    else:
        # macOS / Linux
        os.system(f"lsof -t -i:{port} | xargs kill -9 2>/dev/null || true")


def main():
    parser = argparse.ArgumentParser(
        description="figma-ppt: Start local slide server and output capture plan"
    )
    parser.add_argument("--output-dir", default="./slide-output", help="Slide output directory")
    parser.add_argument("--port",       default=7890, type=int,   help="HTTP server port")
    parser.add_argument("--kill-only",  action="store_true",      help="Kill the server on this port and exit")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    port    = args.port

    # Kill-only mode
    if args.kill_only:
        kill_port(port)
        print(json.dumps({"status": "killed", "port": port}))
        return

    # Kill any existing process on this port
    if port_in_use(port):
        print(f"[serve] Port {port} in use. Killing existing process...", file=sys.stderr)
        kill_port(port)
        time.sleep(1)

    # Start HTTP server
    if not out_dir.exists():
        print(f"ERROR: Output directory not found: {out_dir}", file=sys.stderr)
        sys.exit(1)

    server_cmd = [
        sys.executable, "-m", "http.server", str(port),
        "--directory", str(out_dir.resolve()),
        "--bind", "127.0.0.1",
    ]

    proc = subprocess.Popen(
        server_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to start
    for _ in range(20):
        time.sleep(0.3)
        if port_in_use(port):
            break
    else:
        print("ERROR: Server failed to start.", file=sys.stderr)
        proc.terminate()
        sys.exit(1)

    # Load slide URLs
    urls_path = out_dir / "slide-urls.json"
    if not urls_path.exists():
        print(f"ERROR: slide-urls.json not found in {out_dir}", file=sys.stderr)
        proc.terminate()
        sys.exit(1)

    with open(urls_path, encoding="utf-8") as f:
        url_data = json.load(f)

    # Rebuild URLs with current port (in case default changed)
    for slide in url_data["slides"]:
        fname = slide["file"]
        slide["url"] = f"http://localhost:{port}/slides/{fname}"

    # Output result for Claude
    result = {
        "status": "ready",
        "pid":    proc.pid,
        "port":   port,
        "base_url": f"http://localhost:{port}",
        "title":  url_data["title"],
        "slide_count": len(url_data["slides"]),
        "slides": url_data["slides"],
        "kill_command": f"python skills/figma-ppt/scripts/serve-and-capture.py --kill-only --port {port}",
        "instructions": (
            "Server is running. Call generate_figma_design for each slide URL in order. "
            "After all captures are done, run the kill_command to stop the server."
        ),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
