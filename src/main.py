import uvicorn  # noqa: F401

from src import app  # noqa: F401
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL,
    )
