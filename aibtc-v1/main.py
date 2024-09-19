import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from utils.session import generate_crew_mapping
import streamlit.web.bootstrap as bootstrap
from streamlit.web.server import Server

# Create the main FastAPI application
app = FastAPI()

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

# Initialize Streamlit
streamlit_script_path = "aibtc-v1/streamlit_app.py"
streamlit_config = {
    "server.port": 8501,
    "server.address": "0.0.0.0",
    "server.headless": True,
    "server.runOnSave": False,
    "server.enableCORS": False,
    "server.enableXsrfProtection": False,
}

bootstrap_streamlit = lambda script_path: bootstrap.run(script_path, **streamlit_config)
streamlit_server = Server(bootstrap_streamlit, streamlit_script_path)

# Mount Streamlit app
streamlit_app = WSGIMiddleware(streamlit_server.app)


@app.middleware("http")
async def router_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        response = await call_next(request)
    else:
        response = await streamlit_app(request.scope, request.receive, request.send)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
