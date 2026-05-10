from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "学生积分管理系统"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # 数据库 - 环境变量覆盖，默认 SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./student_points.db"

    # JWT
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # CORS - 环境变量覆盖
    CORS_ORIGINS_STR: str = "http://localhost:5173,http://localhost:3000"

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [s.strip() for s in self.CORS_ORIGINS_STR.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
