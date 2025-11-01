"""
Claude Repo Chat - FastAPI Backend
Browser-based Claude interface for secure repository access
"""

import os
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import structlog

from app.terminal import TmuxTerminal

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

app = FastAPI(
    title="Claude Repo Chat",
    description="Browser-based Claude interface for secure repository access",
    version="0.1.0",
)

# CORS middleware (configure properly in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
TMUX_SESSION = os.getenv("TMUX_SESSION")
ENABLE_TERMINAL = os.getenv("ENABLE_TERMINAL", "false").lower() == "true"
TERMINAL_SHELL = os.getenv("TERMINAL_SHELL", "/bin/bash")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "claude-repo-chat"}


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """Serve the terminal interface"""
    if not ENABLE_TERMINAL:
        return """
        <html>
            <head><title>Claude Repo Chat</title></head>
            <body>
                <h1>Claude Repo Chat</h1>
                <p>Terminal access is disabled for this instance.</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """

    # Read the terminal HTML template
    html_path = Path(__file__).parent / "static" / "terminal.html"
    if html_path.exists():
        return html_path.read_text()

    # Fallback inline HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terminal - Claude Repo Chat</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.min.css" />
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #000;
                font-family: monospace;
            }
            #terminal {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
            }
        </style>
    </head>
    <body>
        <div id="terminal"></div>
        <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.min.js"></script>
        <script>
            const term = new Terminal({
                cursorBlink: true,
                theme: {
                    background: '#000000',
                    foreground: '#ffffff'
                }
            });
            const fitAddon = new FitAddon.FitAddon();
            term.loadAddon(fitAddon);
            term.open(document.getElementById('terminal'));
            fitAddon.fit();

            // WebSocket connection
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${location.host}/ws/terminal`);

            ws.binaryType = 'arraybuffer';

            ws.onopen = () => {
                console.log('Connected to terminal');

                // Send initial size
                ws.send(JSON.stringify({
                    type: 'resize',
                    rows: term.rows,
                    cols: term.cols
                }));
            };

            ws.onmessage = (event) => {
                if (event.data instanceof ArrayBuffer) {
                    const uint8Array = new Uint8Array(event.data);
                    term.write(uint8Array);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                term.write('\r\n\x1b[31mConnection error\x1b[0m\r\n');
            };

            ws.onclose = () => {
                term.write('\r\n\x1b[33mConnection closed\x1b[0m\r\n');
            };

            // Send data from terminal to WebSocket
            term.onData((data) => {
                ws.send(new TextEncoder().encode(data));
            });

            // Handle resize
            window.addEventListener('resize', () => {
                fitAddon.fit();
                ws.send(JSON.stringify({
                    type: 'resize',
                    rows: term.rows,
                    cols: term.cols
                }));
            });

            // Initial fit
            setTimeout(() => {
                fitAddon.fit();
                ws.send(JSON.stringify({
                    type: 'resize',
                    rows: term.rows,
                    cols: term.cols
                }));
            }, 100);
        </script>
    </body>
    </html>
    """


@app.websocket("/ws/terminal")
async def terminal_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for terminal access"""
    if not ENABLE_TERMINAL:
        await websocket.close(code=1008, reason="Terminal access disabled")
        return

    await websocket.accept()

    logger.info(
        "terminal_connection",
        session=TMUX_SESSION,
        client=websocket.client,
    )

    terminal = TmuxTerminal(
        websocket=websocket,
        session_name=TMUX_SESSION,
        shell=TERMINAL_SHELL,
    )

    try:
        await terminal.start()
    except Exception as e:
        logger.error("terminal_error", error=str(e))
        await websocket.close(code=1011, reason=f"Terminal error: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
