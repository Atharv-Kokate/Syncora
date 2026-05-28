# Syncora Collaboration Service

This is the real-time WebSocket state synchronization engine for Syncora. It uses the industry-standard Yjs CRDT formulation.

## Architecture

This microservice does not use a direct relational database. Instead, it relies on two external integrations:
1. **Redis Pub/Sub**: Horizontal websocket scaling. When a user connects to Pod A, and another binds to Pod B, their document binary stream is bridged via Redis Pub/Sub channels (`doc:<uuid>`).
2. **Docs Service HTTP API**: Long-term state persistence. Active CRDT states are flushed out of memory into permanent PostgreSQL JSONB storage every 30 seconds via the `persistence_worker`.

### Protocol

We accept bare TCP WebSocket connections upgraded via the Gateway. Communication occurs via raw binary `Uint8Array` fragments following the `y-websocket` specification.

### Local Development

1. Setup environment
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run dependencies (Ensure Redis and Docs Service are running locally)
   ```bash
   # Run redis on default port 6379
   docker run -p 6379:6379 redis:alpine
   ```

3. Spin up Server
   ```bash
   uvicorn app.main:app --reload --port 8003
   ```
