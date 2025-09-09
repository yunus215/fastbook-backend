from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


# di dalam middleware tidak bisa raise http exception, harus return jsonresponse
# jalannya dari middleware terakhir ke middleware pertama yang didaftarkan
def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        # print("start the request at:", start_time)

        response = await call_next(request)

        processing_time = time.time() - start_time
        # print("processed after:", processing_time)

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

        print(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "fastbook-api-dc03.onrender.com",
            "0.0.0.0",
        ],
    )
