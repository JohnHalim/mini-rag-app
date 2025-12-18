from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Define metrics:
REAUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        start_time = time.time()
        
        # Process the request:
        response = await call_next(request)
        
        # Record metrics after request is processed
        duration = time.time() - start_time
        endpoint = request.url.path
        
        REQUEST_LATENCY.lables(method=request.method, endpoint=endpoint).observe(duration)
        REAUEST_COUNT.lables(method=request.method, endpoint=endpoint, status=response.status_code).inc()
        
        return response
    

def setup_metrics(app: FastAPI):
    """
    Setup Prometheus metrics middleware and endpoint
    """
    # Add prometheus Middleware
    app.add_middleware(PrometheusMiddleware)
    
    @app.get("/Hfaih_B242g_sdFlv", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)    