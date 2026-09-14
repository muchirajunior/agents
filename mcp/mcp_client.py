#!/usr/bin/env python3
"""
MCP Client with HTML Output - Flask Version
A simple web-based client for interacting with MCP servers using Flask
"""

import json
import sys
import requests
from urllib.parse import urljoin
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Configuration
MCP_SERVER_URL = "http://localhost:8000"


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Client</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f; color: #e0e0e0; min-height: 100vh; padding-bottom: 60px;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; margin-bottom: 30px; color: #00d4ff; font-size: 2rem; }
        .card {
            background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 20px; margin-bottom: 20px;
        }
        .card h2 { color: #00d4ff; margin-bottom: 15px; font-size: 1.1rem; }
        input, textarea {
            width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px;
            background: #0f0f0f; color: #e0e0e0; font-size: 14px; margin-bottom: 10px;
        }
        textarea { min-height: 80px; resize: vertical; }
        button {
            padding: 12px 24px; border: none; border-radius: 8px; background: #00d4ff;
            color: #0f0f0f; font-weight: 600; cursor: pointer;
        }
        button:hover { background: #33ddff; }
        .result-box {
            background: #0a0a0a; border: 1px solid #333; border-radius: 8px; padding: 15px;
            margin-top: 15px; white-space: pre-wrap; font-family: monospace; font-size: 13px;
            max-height: 400px; overflow-y: auto; display: none;
        }
        .result-box.success { border-color: #00d4ff; }
        .result-box.error { border-color: #ff4444; color: #ff8888; }
        .status-bar {
            background: #0a0a0a; border-top: 1px solid #333; padding: 10px 20px;
            position: fixed; bottom: 0; left: 0; right: 0; display: flex;
            justify-content: space-between; align-items: center;
        }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #ff4444; }
        .status-dot.connected { background: #00ff44; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 MCP Client</h1>
        
        <div class="card">
            <h2>⚙️ Server Configuration</h2>
            <input type="text" id="serverUrl" placeholder="http://localhost:8000" value="{{ server_url }}">
            <button onclick="connectServer()">Connect</button>
            <div id="connStatus" style="margin-top:10px;font-size:14px;"></div>
        </div>

        <div class="card">
            <h2>📖 Read File</h2>
            <input type="text" id="readPath" placeholder="Enter file path">
            <button onclick="readFile()">Read File</button>
            <div id="readResult" class="result-box"></div>
        </div>

        <div class="card">
            <h2>📂 List Files</h2>
            <input type="text" id="listPath" placeholder="Enter directory path (default: current)">
            <button onclick="listFiles()">List Files</button>
            <div id="listResult" class="result-box"></div>
        </div>

        <div class="card">
            <h2>✏️ Edit File</h2>
            <input type="text" id="editPath" placeholder="Enter file path">
            <textarea id="oldText" placeholder="Old text to replace"></textarea>
            <textarea id="newText" placeholder="New text to replace with"></textarea>
            <button onclick="editFile()">Edit File</button>
            <div id="editResult" class="result-box"></div>
        </div>
    </div>

    <div class="status-bar">
        <div style="display:flex;align-items:center;gap:8px;">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">Disconnected</span>
        </div>
        <div id="spinner" style="display:none;"><div class="spinner"></div></div>
    </div>

    <script>
        let serverUrl = '{{ server_url }}';
        let isConnected = false;

        function showLoading(show) {
            document.getElementById('spinner').style.display = show ? 'block' : 'none';
        }

        function showResult(elementId, content, isError = false) {
            const el = document.getElementById(elementId);
            el.textContent = content;
            el.className = 'result-box ' + (isError ? 'error' : 'success');
            el.style.display = 'block';
        }

        function updateStatus(connected) {
            isConnected = connected;
            const dot = document.getElementById('statusDot');
            const text = document.getElementById('statusText');
            if (connected) {
                dot.classList.add('connected');
                text.textContent = 'Connected';
            } else {
                dot.classList.remove('connected');
                text.textContent = 'Disconnected';
            }
        }

        async function connectServer() {
            serverUrl = document.getElementById('serverUrl').value.trim() || 'http://localhost:8000';
            showLoading(true);
            try {
                const resp = await fetch('/api/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({server_url: serverUrl})
                });
                const data = await resp.json();
                if (data.success) {
                    updateStatus(true);
                    showResult('connStatus', '✅ Connected to MCP server!', false);
                } else {
                    throw new Error(data.error || 'Connection failed');
                }
            } catch (err) {
                updateStatus(false);
                showResult('connStatus', `❌ ${err.message}`, true);
            } finally {
                showLoading(false);
            }
        }

        async function callTool(toolName, args, resultElement) {
            if (!isConnected) {
                alert('Please connect to server first!');
                return;
            }
            showLoading(true);
            try {
                const resp = await fetch('/api/call', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        server_url: serverUrl,
                        tool_name: toolName,
                        arguments: args
                    })
                });
                const data = await resp.json();
                if (data.success) {
                    showResult(resultElement, data.result, false);
                } else {
                    showResult(resultElement, data.error || 'Tool call failed', true);
                }
            } catch (err) {
                showResult(resultElement, `Error: ${err.message}`, true);
            } finally {
                showLoading(false);
            }
        }

        function readFile() {
            const path = document.getElementById('readPath').value.trim();
            if (!path) return alert('Please enter a file path');
            callTool('read_file', {path}, 'readResult');
        }

        function listFiles() {
            const path = document.getElementById('listPath').value.trim() || '.';
            callTool('list_files', {path}, 'listResult');
        }

        function editFile() {
            const path = document.getElementById('editPath').value.trim();
            const oldText = document.getElementById('oldText').value;
            const newText = document.getElementById('newText').value;
            if (!path) return alert('Please enter a file path');
            callTool('edit_file', {path, old_text: oldText, new_text: newText}, 'editResult');
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template_string(HTML_TEMPLATE, server_url=MCP_SERVER_URL)


@app.route('/api/test', methods=['POST'])
def test_connection():
    """Test connection to MCP server"""
    try:
        data = request.get_json()
        server_url = data.get('server_url', MCP_SERVER_URL)
        
        response = requests.get(f"{server_url}/tools", timeout=5)
        
        if response.status_code == 200:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': f'Server returned {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/call', methods=['POST'])
def call_tool():
    """Call a tool on the MCP server"""
    try:
        data = request.get_json()
        server_url = data.get('server_url', MCP_SERVER_URL)
        tool_name = data['tool_name']
        arguments = data['arguments']
        
        payload = {'arguments': arguments}
        response = requests.post(
            f"{server_url}/tools/{tool_name}",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({'success': True, 'result': result.get('result', '')})
        else:
            return jsonify({
                'success': False,
                'error': f'Server returned {response.status_code}: {response.text}'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Client with HTML Output')
    parser.add_argument('--mcp-server', default='http://localhost:8000',
                        help='MCP server URL (default: http://localhost:8000)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Web server port (default: 8080)')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host to bind to (default: 127.0.0.1)')
    
    args = parser.parse_args()
    
    global MCP_SERVER_URL
    MCP_SERVER_URL = args.mcp_server
    
    print(f"🌐 MCP Client with HTML Output")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🖥️  Web Interface: http://{args.host}:{args.port}")
    print(f"🔗 MCP Server: {MCP_SERVER_URL}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Open your browser and navigate to http://{args.host}:{args.port}")
    print()
    
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
