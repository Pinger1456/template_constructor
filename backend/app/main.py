from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .api.templates import router as templates_router
import uvicorn

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


app.include_router(templates_router, prefix="/api")
# --- Настройка CORS: переместите это сюда, до include_router ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
# ------------------------------------------------------------

# Регистрируем API-маршруты
app.include_router(templates_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to DocBuilder!"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
