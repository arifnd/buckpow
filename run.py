import uvicorn
from src.config import settings

if __name__ == '__main__':
    uvicorn.run(
        'src:app',
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL,
    )
