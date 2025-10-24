from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import backend.api.log_controller as log_controller

app = FastAPI(title="Log Analytics API", version="1.0")

# Add CORS middleware to allow frontend to access the backend
origins = [
    "http://localhost:5173",  # Your frontend URL (for local development)
    # You can add more origins here if you have other environments (e.g. production URL)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows CORS from the specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Register API routers
app.include_router(log_controller.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
