"""应用配置：从仓库根目录 .env 读取，密码与密钥不进 Git。"""
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# 仓库根目录 = backend/app/config.py 向上两级
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """环境变量与前缀 ALBUM_ 对应，见仓库根目录 .env.example。"""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    album_db_port: int = 55432
    album_db_password: str
    album_jwt_secret: str
    album_session_minutes: int = 120
    album_demo_password: str = "album-demo-123"
    album_admin_password: str = "album-admin-123"

    @property
    def database_url(self) -> str:
        password = quote_plus(self.album_db_password)
        return (
            f"postgresql+psycopg://album_app:{password}"
            f"@127.0.0.1:{self.album_db_port}/electronic_photo_album"
        )

    @property
    def uploads_root(self) -> Path:
        return REPO_ROOT / "uploads"

    @property
    def allowed_origins(self) -> list[str]:
        """开发期前端同源代理的来源；写请求核对 Origin 时使用。"""
        return ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
