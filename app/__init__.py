from fastapi import FastAPI
from app.routes.routes import router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


def create_app():

    app = FastAPI()

    app.mount("/assets", StaticFiles(directory="./frontend/dist/assets"), name="assets")
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    # Register your routes with the app
    app.include_router(router)

    return app
