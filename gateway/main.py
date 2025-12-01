import httpx
from fastapi import FastAPI, Request, Response, HTTPException

app = FastAPI()

# Mapping of path prefixes to service URLs
SERVICE_MAP = {
    "providers": "http://providers_service:8000",
    "equipment": "http://equipment_service:8000",
    "maintenance": "http://maintenance_service:8000",
    "reports": "http://reports_service:8000",
}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    # Determine which service to route to
    path_parts = path.split("/")
    if not path_parts or path_parts[0] == "":
        return {"message": "API Gateway Ready"}
    
    service_name = path_parts[0]
    
    if service_name not in SERVICE_MAP:
         raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
         
    target_url = f"{SERVICE_MAP[service_name]}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers,
                content=await request.body(),
                params=request.query_params,
            )
            return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
