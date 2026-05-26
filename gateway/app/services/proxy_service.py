import httpx
from fastapi import Request, HTTPException, status
from fastapi.responses import StreamingResponse
import structlog
from app.core.constants import HOP_BY_HOP_HEADERS

log = structlog.get_logger()

async def forward_request(request: Request, target_url: str, client: httpx.AsyncClient) -> StreamingResponse:
    """
    Forwards an incoming FastAPI request to the target downstream microservice.
    Uses StreamingResponse to efficiently proxy chunked data or large payloads
    without buffering them entirely in the gateway's memory.
    """
    log.info("forwarding_request", target_url=target_url, method=request.method)
    
    # 1. Structure the destination URL
    # Combine the downstream service URL with the original request's path and query string.
    url = httpx.URL(target_url).copy_with(
        query=request.url.query.encode("utf-8")
    )
    
    # 2. Filter Headers
    # We must not forward hop-by-hop headers originally meant for the gateway.
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host":
            headers[key] = value
            
    # Inject our correlation ID to the downstream service if it's somehow missing,
    # though our middleware currently handles generating it on the gateway side.
    if "x-correlation-id" not in {k.lower() for k in headers.keys()}:
        headers["x-correlation-id"] = request.headers.get("X-Correlation-ID", "")        
    # Inject user identity into downstream headers if auth was performed at the gateway
    if hasattr(request.state, "user_payload") and request.state.user_payload:
        user_id = request.state.user_payload.get("sub")
        if user_id:
            headers["x-user-id"] = str(user_id)            
    # 3. Read body asynchronously
    # (Since this is a standard REST gateway for now, we read the body into memory. 
    # For massive file uploads, we'd want to stream the request body as well).
    body = await request.body()
    
    # 4. Fire the request
    try:
        # Build the request exactly as the client sent it
        req = client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )
        
        # Stream the response instead of waiting for the full downstream payload
        response = await client.send(req, stream=True)
        
        # Filter return headers
        response_headers = {}
        for key, value in response.headers.items():
            if key.lower() not in HOP_BY_HOP_HEADERS:
                response_headers[key] = value

        # Create an async generator to stream chunks back to the original client
        async def stream_generator():
            async for chunk in response.aiter_raw():
                yield chunk
            await response.aclose()
            
        return StreamingResponse(
            stream_generator(),
            status_code=response.status_code,
            headers=response_headers,
            # Pass through the content type if present
            media_type=response.headers.get("content-type")
        )
        
    except httpx.ConnectError as e:
        log.error("upstream_connection_error", target_url=str(url), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail="Upstream service is unreachable."
        )
    except httpx.TimeoutException as e:
        log.error("upstream_timeout_error", target_url=str(url), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, 
            detail="Upstream service timed out."
        )
    except Exception as e:
        log.error("upstream_proxy_error", target_url=str(url), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An expected error occurred while proxying the request."
        )
