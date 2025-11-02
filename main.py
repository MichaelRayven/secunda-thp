from fastapi import FastAPI
from router.organizations_router import organizations_router

app = FastAPI()

app.include_router(organizations_router)
