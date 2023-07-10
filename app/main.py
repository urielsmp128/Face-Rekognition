from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.image import image
from app.routes.person import person
from app.routes.user import user

app = FastAPI(
    title="Photo AI API",
    description="REST API for Photo AI Platform",
    version="1.0.0",
)

app.include_router(image)
app.include_router(person)
app.include_router(user)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "API running..."}
    # return settings.VERSION
