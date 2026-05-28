from fastapi import WebSocket
import structlog
from typing import Dict, List
import uuid

logger = structlog.get_logger()

class WebSocketManager:
    """
    Manages active WebSocket connections to this specific server pod.
    Grouped by document_id.
    """
    def __init__(self):
        # Format: { "document_id": { "uuid": WebSocket } }
        self.active_documents: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, document_id: str) -> str:
        """Accepts a WebSocket connection and registers it."""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        if document_id not in self.active_documents:
            self.active_documents[document_id] = {}
            
        self.active_documents[document_id][connection_id] = websocket
        logger.info("websocket_connected", connection_id=connection_id, document_id=document_id)
        
        return connection_id

    def disconnect(self, document_id: str, connection_id: str):
        """Removes a connection from the tracking pool."""
        if document_id in self.active_documents:
            if connection_id in self.active_documents[document_id]:
                del self.active_documents[document_id][connection_id]
                logger.info("websocket_disconnected", connection_id=connection_id, document_id=document_id)
                
            # If the room is now empty, delete the room
            if not self.active_documents[document_id]:
                del self.active_documents[document_id]
                logger.info("document_room_cleaned", document_id=document_id)

    async def broadcast_to_local_room(self, document_id: str, message: bytes, sender_connection_id: str = None):
        """
        Broadcasts a binary payload to all local WebSockets in a document room.
        Optinally skips the sender if sender_connection_id is provided.
        """
        if document_id in self.active_documents:
            connections_to_remove = []
            
            for cid, websocket in self.active_documents[document_id].items():
                if cid == sender_connection_id:
                    continue # Don't echo back to the person who just sent the edit
                    
                try:
                    await websocket.send_bytes(message)
                except Exception as e:
                    logger.warning("websocket_send_failed", connection_id=cid, error=str(e))
                    connections_to_remove.append(cid)
                    
            # Clean up broken pipes
            for cid in connections_to_remove:
                self.disconnect(document_id, cid)

# Global singleton instance
ws_manager = WebSocketManager()