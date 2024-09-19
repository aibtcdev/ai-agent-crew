from fastapi.responses import RedirectResponse
import uvicorn
from fastapi import FastAPI, Request
from utils.session import generate_crew_mapping
import subprocess
import os

# Create the main FastAPI application
app = FastAPI()

# Generate the crew mapping
crew_mapping = generate_crew_mapping()

# Create API router
for crew_name, crew_info in crew_mapping.items():
    crew_class = crew_info["class"]
    crew_instance = crew_class()
    app.include_router(crew_instance.create_api_endpoint(), prefix=f"/api/{crew_name}")

# Middleware for routing to API or Streamlit
@app.middleware("http")
async def router_middleware(request: Request, call_next):
    # Handle FastAPI-related paths
    fastapi_paths = ["/", "/docs", "/redoc", "/openapi.json"]
    
    if request.url.path.startswith("/api/"):
        # If it's an API request, handle it by FastAPI
        response = await call_next(request)
    elif any(request.url.path.startswith(path) for path in fastapi_paths):
        # If it's a request to FastAPI routes like root, docs, or openapi
        response = await call_next(request)
    else:
        # Redirect all other traffic to Streamlit
        response = RedirectResponse(url="http://localhost:8501" + request.url.path)
    
    return response

# Start the Streamlit app in a subprocess
def run_streamlit():
    streamlit_script_path = os.path.join(os.getcwd(), "streamlit_app.py")
    subprocess.Popen(
        [
            "streamlit", "run", streamlit_script_path, 
            "--server.port=8501", 
            "--server.enableCORS=false"
        ],
    )

if __name__ == "__main__":
    # Run Streamlit as a background process
    run_streamlit()
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8080)
