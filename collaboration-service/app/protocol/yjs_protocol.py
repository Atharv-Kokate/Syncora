"""
Yjs y-websocket Protocol Constants

This file defines the binary message types used by the y-websocket provider.
When the client sends binary messages, the very first byte defines the message type.
"""

# Yjs Message Types (First Byte)
MSG_SYNC = 0              # Synchronization payload
MSG_AWARENESS = 1         # Cursor / Selection / Online status payload
MSG_AUTH = 2              # Authentication payload
MSG_QUERY_AWARENESS = 3   # Request for awareness states

# Sync Message Sub-types (Second Byte when MSG_SYNC)
SYNC_STEP_1 = 0           # Client asks server for missing state
SYNC_STEP_2 = 1           # Server responds with missing state (or vice-versa)
SYNC_UPDATE = 2           # Standard delta update (e.g. a user typed a character)

def get_message_type(message: bytes) -> int:
    """Returns the primary message type from a raw Yjs binary message."""
    if not message:
        return -1
    return message[0]
