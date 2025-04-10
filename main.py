from fastapi import FastAPI
from core.routes import api_router

app = FastAPI()
app.include_router(api_router)

# You can also add global middleware, exception handlers, etc., here if needed.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 