from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ─── App ──────────────────────────────────────
    APP_ENV: str = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://127.0.0.1:5173"

    # ─── Paths (all on E:) ────────────────────────
    DATA_ROOT: str = "E:/IDE/Eternal-Mind/data"
    MODEL_ROOT: str = "E:/IDE/Eternal-Mind/models"
    SQLITE_PATH: str = "E:/IDE/Eternal-Mind/data/database/eternal_mind.db"
    CHROMA_PATH: str = "E:/IDE/Eternal-Mind/data/chroma"

    # ─── LLM ──────────────────────────────────────
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "qwen2.5:3b"
    LLM_BASE_URL: str = "http://127.0.0.1:11434"
    LLM_TEMPERATURE: float = 0.4
    LLM_CONTEXT_LENGTH: int = 2048

    # ─── Embeddings (Stage 3) ─────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ─── Speech (Stage 6) ─────────────────────────
    STT_MODEL: str = "base"
    STT_DEVICE: str = "cpu"
    STT_COMPUTE_TYPE: str = "int8"
    TTS_ENGINE: str = "piper"
    TTS_VOICE: str = ""

    # ─── Logging ──────────────────────────────────
    LOG_LEVEL: str = "INFO"
    STORE_MESSAGE_BODIES_IN_LOGS: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a single instance to be imported across the app
settings = Settings()