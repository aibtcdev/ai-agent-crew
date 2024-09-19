import subprocess
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from utils.session import generate_crew_mapping

# Create the main FastAPI application
app = FastAPI()

# Run Streamlit as a subprocess
streamlit_process = subprocess.Popen(
    [
        "streamlit",
        "run",
        "aibtc-v1/streamlit_app.py",
        "--server.port",
        "8501",
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",
        "--server.runOnSave",
        "false",
        "--server.enableCORS",
        "false",
        "--server.enableWebsocketCompression",
        "false",
    ]
)

# Create API router
api_router = FastAPI()

# Generate the crew mapping
crew_mapping = generate_crew_mapping()

# Add endpoints for each crew
for crew_name, crew_info in crew_mapping.items():
    crew_class = crew_info["class"]
    crew_instance = crew_class()
    api_router.include_router(crew_instance.create_api_endpoint(), tags=[crew_name])

# Include the API routes
app.mount("/api", api_router)

# Mount Streamlit app
from streamlit.web.server import Server

streamlit_app = WSGIMiddleware(Server(streamlit_process.pid).app)


@app.middleware("http")
async def router_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        response = await call_next(request)
    else:
        response = await streamlit_app(request.scope, request.receive, request.send)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
