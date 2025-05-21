from pydantic import BaseSettings # type: ignore

class Settings(BaseSettings):
    UPLOAD_DIR: str = "data/uploads"
    DATABASE_URL: str = "sqlite:///./data/storage-db/cvflow.db"
    RABBITMQ_HOST: str = "rabbitmq"
    PARSER_QUEUE: str = "parser_queue"
    KEYWORD_QUEUE: str = "keyword_queue"
    FEEDBACK_QUEUE: str = "feedback_queue"
    JOBMATCH_QUEUE: str = "jobmatch_queue"
    NOTIFICATION_QUEUE: str = "notification_queue"

    class Config:
        env_file = ".env"  # Cargar desde archivo .env si existe

settings = Settings()
