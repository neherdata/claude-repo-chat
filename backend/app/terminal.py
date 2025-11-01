"""
Terminal WebSocket handler for tmux session attachment
"""

import asyncio
import os
import pty
import select
import struct
import termios
from typing import Optional

import structlog
from fastapi import WebSocket, WebSocketDisconnect

logger = structlog.get_logger(__name__)


class TmuxTerminal:
    """Manages a tmux terminal session over WebSocket"""

    def __init__(
        self,
        websocket: WebSocket,
        session_name: Optional[str] = None,
        shell: str = "/bin/bash",
    ):
        self.websocket = websocket
        self.session_name = session_name
        self.shell = shell
        self.pid: Optional[int] = None
        self.fd: Optional[int] = None

    async def start(self) -> None:
        """Start the terminal session"""
        logger.info(
            "starting_terminal",
            session_name=self.session_name,
            shell=self.shell,
        )

        # Spawn tmux attach or regular shell
        if self.session_name:
            cmd = ["tmux", "attach-session", "-t", self.session_name]
        else:
            cmd = [self.shell]

        # Create PTY
        self.pid, self.fd = pty.fork()

        if self.pid == 0:
            # Child process - exec the command
            os.execvp(cmd[0], cmd)
        else:
            # Parent process - handle I/O
            await self._handle_io()

    async def _handle_io(self) -> None:
        """Handle bidirectional I/O between WebSocket and PTY"""
        try:
            # Create tasks for both directions
            read_task = asyncio.create_task(self._read_from_pty())
            write_task = asyncio.create_task(self._write_to_pty())

            # Wait for either task to complete (likely on disconnect)
            done, pending = await asyncio.wait(
                [read_task, write_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            logger.error("terminal_io_error", error=str(e))
        finally:
            self._cleanup()

    async def _read_from_pty(self) -> None:
        """Read from PTY and send to WebSocket"""
        loop = asyncio.get_event_loop()

        while True:
            try:
                # Wait for data to be available
                ready, _, _ = await loop.run_in_executor(
                    None, select.select, [self.fd], [], [], 0.1
                )

                if ready:
                    # Read from PTY
                    data = await loop.run_in_executor(None, os.read, self.fd, 10240)
                    if not data:
                        break

                    # Send to WebSocket
                    await self.websocket.send_bytes(data)
                else:
                    # Small delay to prevent busy loop
                    await asyncio.sleep(0.01)

            except OSError:
                # PTY closed
                break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("pty_read_error", error=str(e))
                break

    async def _write_to_pty(self) -> None:
        """Read from WebSocket and write to PTY"""
        loop = asyncio.get_event_loop()

        try:
            while True:
                # Receive from WebSocket
                message = await self.websocket.receive()

                if "bytes" in message:
                    # Binary data - write to PTY
                    await loop.run_in_executor(None, os.write, self.fd, message["bytes"])

                elif "text" in message:
                    # Handle special commands (like resize)
                    import json

                    try:
                        cmd = json.loads(message["text"])
                        if cmd.get("type") == "resize":
                            await self._resize(cmd["rows"], cmd["cols"])
                    except (json.JSONDecodeError, KeyError):
                        # Not a command, treat as text input
                        data = message["text"].encode("utf-8")
                        await loop.run_in_executor(None, os.write, self.fd, data)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error("pty_write_error", error=str(e))

    async def _resize(self, rows: int, cols: int) -> None:
        """Resize the PTY"""
        try:
            # Set terminal size
            size = struct.pack("HHHH", rows, cols, 0, 0)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: termios.ioctl(self.fd, termios.TIOCSWINSZ, size),
            )
            logger.debug("terminal_resized", rows=rows, cols=cols)
        except Exception as e:
            logger.error("resize_error", error=str(e))

    def _cleanup(self) -> None:
        """Clean up PTY resources"""
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None

        if self.pid is not None:
            try:
                os.waitpid(self.pid, 0)
            except OSError:
                pass
            self.pid = None

        logger.info("terminal_closed", session_name=self.session_name)
