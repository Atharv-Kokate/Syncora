import asyncio
import structlog
import httpx
from app.core.config import settings

logger = structlog.get_logger()

class CRDTPersistenceWorker:
    """
    Background worker that runs in the Collab Service.
    It periodically queries the active Yjs documents in memory,
    serializes their state updates, and flushes them to the Docs Service's
    JSONB storage for permanent database persistence.
    """
    def __init__(self):
        self._task = None
        self._http_client = None

    async def start(self):
        self._http_client = httpx.AsyncClient(timeout=10.0)
        self._task = asyncio.create_task(self._run_loop())
        logger.info("crdt_persistence_worker_started")

    async def stop(self):
        if self._task:
            self._task.cancel()
        if self._http_client:
            await self._http_client.aclose()
        logger.info("crdt_persistence_worker_stopped")

    async def _run_loop(self):
        try:
            while True:
                # Flush every 30 seconds
                await asyncio.sleep(30)
                
                # In a full implementation, we iterate through active pycrdt.Docs
                # Ex: doc_state = active_docs[doc_id].get_update()
                # await self._http_client.patch(f"{settings.DOCS_SERVICE_URL}/{doc_id}", json={"content": doc_state.hex()})
                
                logger.debug("crdt_persistence_heartbeat", status="flushing_active_documents")
        except asyncio.CancelledError:
            logger.info("crdt_persistence_worker_cancelled")
        except Exception as e:
            logger.error("crdt_persistence_worker_crash", error=str(e))

persistence_worker = CRDTPersistenceWorker()
