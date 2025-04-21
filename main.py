from fastapi import FastAPI
from core.routes import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from middleware.tokenAuthentication import AccessTokenAuthenticatorMiddleware
from middleware.allowedHostsMiddleware import AllowedHostsMiddleware
from middleware.timeMeasureMiddleware import ExecutionTimeMiddleware
app = FastAPI()

#Add the CORS middleware with the allowed origin
origins = [
    "http://localhost:3000",
    "http://192.168.1.64:8000",
    "http://127.0.0.1:3000",
    "http://3.110.39.32:8000"
    # "*"
]
allowed_hosts=["*"]   # allowed_hosts=["localhost", "127.0.0.1", "example.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # If we convert it to allow_origins=["*"] it will allow all origins -> so we implemented CORS_ALLOW_ALL_ORIGINS = True from django to fastapi
    allow_credentials=True, # In Django, credentials are allowed implicitly unless explicitly disabled.
    allow_methods=["*"],
    allow_headers=["token", "content-type"],
)

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     print(f"Request: {request.method} {request.url}")
#     response = await call_next(request)
#     return response

# Note that in FastAPI, You can also specify allow_credentials=True to allow credentials in CORS requests.
app.add_middleware(AllowedHostsMiddleware, allowed_hosts)
# Add the custom middleware
app.add_middleware(AccessTokenAuthenticatorMiddleware)
app.add_middleware(ExecutionTimeMiddleware)
# Include all routes
app.include_router(api_router)

# You can also add global middleware, exception handlers, etc., here if needed.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 

    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload