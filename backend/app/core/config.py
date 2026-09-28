"""
Configuração central da aplicação.
Gerencia variáveis de ambiente e constantes.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Motor Biomecânico Paramétrico"
    PROJECT_VERSION: str = "0.1.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    LOG_LEVEL: str = "info"

    # Database
    DATABASE_URL: str = "sqlite:///./motor_biomecanico.db"
    # Exemplo PostgreSQL: "postgresql://user:password@localhost/motor_biomecanico"

    # CORS
    CORS_ORIGINS: list = ["*"]  # Em produção: ["http://localhost:5173"]

    # Features
    ENABLE_LEARNING: bool = True  # Aprendizado contínuo
    ENABLE_PRESSURE_SIMULATION: bool = True  # Simulação de pressão
    ENABLE_3D_EXPORT: bool = True  # Exportação STL

    # Limits
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_CASES_PER_PATIENT: int = 1000
    MAX_SUGGESTIONS_PER_CASE: int = 10

    # Suggestion Engine
    CONFIDENCE_THRESHOLD_MIN: float = 0.65
    CONFIDENCE_THRESHOLD_DEFAULT: float = 0.75

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Paths
    EXPORT_PATH: str = "/tmp/exports"
    UPLOAD_PATH: str = "/tmp/uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global de settings
settings = Settings()
