from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import structlog
from app.services.ws_manager import ws_manager
from app.services.pubsub_manager import pubsub_manager
from app.protocol.yjs_protocol import get_message_type

logger = structlog.get_logger()
router = APIRouter()

@router.websocket("/ws/{document_id}")
async def collaboration_endpoint(websocket: WebSocket, document_id: str, token: str):
    """
    The core Yjs collaboration endpoint.
    Expects binary UIint8Array messages conforming to the Y-Websocket protocol.
    
    Security: The API Gateway intercepts this upgrade request, validates the JWT,
    and we expect the token as a query parameter (since WS headers are limited in browsers).
    """
    
    # 1. Accept and Register Connection locally
    connection_id = await ws_manager.connect(websocket, document_id)
    channel_name = f"doc:{document_id}"

    # 2. Define the Redis Callback for this specific WebSocket
    async def redis_callback(binary_data: bytes):
        """When Redis receives an edit from ANOTHER pod, push it down this WebSocket."""
        try:
            await websocket.send_bytes(binary_data)
        except Exception:
            pass # Disconnection handled in main loop

    # 3. Subscribe this user's callback to the Redis Pub/Sub channel
    await pubsub_manager.subscribe(channel_name, redis_callback)

    try:
        # 4. Listen for binary messages from the Client
        while True:
            # Yjs protocol strictly uses binary WebSockets
            binary_message = await websocket.receive_bytes()
            msg_type = get_message_type(binary_message)
            
            logger.debug("received_yjs_message", 
                         document_id=document_id, 
                         msg_type=msg_type, 
                         size=len(binary_message))

            # Broadcast to local users connected to exactly THIS pod
            await ws_manager.broadcast_to_local_room(
                document_id=document_id, 
                message=binary_message, 
                sender_connection_id=connection_id
            )

            # Broadcast to Redis so OTHER pods can relay it to their local users
            await pubsub_manager.publish(channel_name, binary_message)

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected", connection_id=connection_id)
    except Exception as e:
        logger.error("websocket_loop_error", error=str(e), connection_id=connection_id)
    finally:
        # Cleanup routine
        ws_manager.disconnect(document_id, connection_id)
        await pubsub_manager.unsubscribe(channel_name, redis_callback)
