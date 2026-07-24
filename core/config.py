from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    系统配置类
    从 .env 文件读取配置
    """

    APP_NAME: str = "AI Course Agent Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "dev"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "sqlite:///./data/app.db"

    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    JWT_SECRET_KEY: str = "ai-course-agent-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DASHSCOPE_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-v4"
    EMBEDDING_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    EMBEDDING_DIMENSION: int = 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins(self) -> List[str]:
        """
        将 .env 中的跨域配置字符串转换成列表
        """
        if not self.BACKEND_CORS_ORIGINS:
            return []

        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()