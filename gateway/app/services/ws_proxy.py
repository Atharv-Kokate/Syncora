from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import Response
import httpx
import websockets
import structlog
import asyncio
from typing import Dict, Any, Callable
from urllib.parse import urlparse

from app.core.config import get_settings
from app.services.jwt_service import extract_user_from_token

logger = structlog.get_logger()
settings = get_settings()

class WebSocketProxy:
    """Proxy for WebSocket connections via the Gateway."""
    
    @staticmethod
    async def proxy_ws(
        client_ws: WebSocket, 
        downstream_ws_url: str,
        token: str
    ):
        """
        Validates the user token, accepts the client websocket,
        connects to the downstream microservice, and establishes a pump.
        """
        # 1. Validate JWT (must be passed in query params for WS)
        user_info = None
        if token:
            user_info = extract_user_from_token(token)
            
        if not user_info:
            await client_ws.close(code=1008, reason="Invalid or missing authentication token")
            logger.warning("websocket_proxy_auth_failure", url=downstream_ws_url)
            return

        # 2. Accept client connection
        await client_ws.accept()
        user_id = user_info["sub"]
        logger.info("websocket_proxy_accepted", user_id=user_id, target=downstream_ws_url)

        # 3. Connect to downstream microservice (Forwarding the X-User-ID)
        headers = {
            "X-User-ID": user_id
        }
        
        # We append the original token so the downstream can also log/use if needed
        # but realistically downstream relies strictly on the X-User-ID header if it can,
        # or we just pass the JWT down for it to extract locally based on our routes.
        # Note: python websockets library doesn't easily set standard headers like X-User-Id
        # the way HTTP HTTP/1.1 does, so the query string token is usually safely forwarded.
        target_url = f"{downstream_ws_url}?token={token}"

        try:
            async with websockets.connect(target_url, extra_headers=headers) as backend_ws:
                # 4. Establish bi-directional pump
                await WebSocketProxy._pump(client_ws, backend_ws)
                
        except websockets.exceptions.WebSocketException as e:
            logger.error("downstream_websocket_error", target=downstream_ws_url, error=str(e))
            try:
                await client_ws.close(code=1011, reason="Gateway downstream connection failed")
            except Exception:
                pass
        except Exception as e:
            logger.error("websocket_proxy_unhandled_error", error=str(e))
        finally:
            logger.info("websocket_proxy_closed", user_id=user_id, target=downstream_ws_url)

    @staticmethod
    async def _pump(client_ws: WebSocket, backend_ws: websockets.WebSocketClientProtocol):
        """Pumps messages bi-directionally between client HTTP/FastAPI and downstream websockets."""
        
        async def read_from_client():
            try:
                while True:
                    message = await client_ws.receive()
                    if "bytes" in message:
                        await backend_ws.send(message["bytes"])
                    elif "text" in message:
                        await backend_ws.send(message["text"])
                    elif message["type"] == "websocket.disconnect":
                        await backend_ws.close()
                        break
            except WebSocketDisconnect:
                await backend_ws.close()
            except Exception as e:
                logger.error("pump_read_from_client_error", error=str(e))
                await backend_ws.close()

        async def read_from_backend():
            try:
                async for message in backend_ws:
                    if isinstance(message, bytes):
                        await client_ws.send_bytes(message)
                    else:
                        await client_ws.send_text(message)
            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                logger.error("pump_read_from_backend_error", error=str(e))
                try:
                    await client_ws.close()
                except Exception:
                    pass

        # Run both pumps concurrently
        await asyncio.gather(
            read_from_client(),
            read_from_backend()
        )

ws_proxy = WebSocketProxy()
