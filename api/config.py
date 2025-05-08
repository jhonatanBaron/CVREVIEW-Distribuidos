# api/config.py
import os

class Settings:
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/storage-db/cvflow.db")

settings = Settings()
