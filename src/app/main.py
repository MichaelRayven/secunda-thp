from fastapi import FastAPI
from router.organizations_router import organizations_router
import uvicorn


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(organizations_router)
    return app


if __name__ == '__main__':
    uvicorn.run(factory=create_app, host='0.0.0.0', port=8000)
