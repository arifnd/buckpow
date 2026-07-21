import os
import uvicorn

from src.config import settings
from src import app

if __name__ == '__main__':
    uvicorn.run(
        'src.main:app',
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL,
    )
