import uvicorn
from fastapi import FastAPI

from app.presentation.api.routes.organisation import organization_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(organization_router)
    return app


if __name__ == '__main__':
    uvicorn.run(app=create_app(), port=8000)
