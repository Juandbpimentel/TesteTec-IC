# logging_utils.py
from fastapi import Request
import logging
import logging.config
import yaml
from fastapi.responses import JSONResponse
import os

from error_response import ErrorResponse

class IgnoreWatchfilesFilter(logging.Filter):
    def filter(self, record):
        return "watchfiles.main" not in record.name

def setup_logging():
    logging_config = {
        'version': 1,
        'formatters': {
            'default': {
                'format': os.getenv('LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            },
        },
        'filters': {
            'ignore_watchfiles': {
                '()': IgnoreWatchfilesFilter,
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': os.getenv('LOGGING_FILE', 'app.log'),
                'filters': ['ignore_watchfiles'],
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'filters': ['ignore_watchfiles'],
            },
        },
        'root': {
            'level': os.getenv('LOGGING_LEVEL', 'INFO'),
            'handlers': ['file', 'console'],
        },
    }
    logging.config.dictConfig(logging_config)

async def log_exceptions_middleware(request: Request, call_next):
    try:
        logging.info(f"Request {request.method} {request.url} received, body: {await request.body()}")
        response = await call_next(request)
        logging.info(f"Request {request.method} {request.url} processed: {response.status_code}")
        return response
    except Exception as exc:
        if not isinstance(exc, ErrorResponse):
            logging.error(f"Unhandled error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Erro Interno do Servidor - Tente Novamente", "error": str(exc)}
            )
        exc = ErrorResponse(exc.status_code, exc.message)
        return exc.to_json_response()