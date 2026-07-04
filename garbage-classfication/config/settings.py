from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置（注意库名是 garbage_classfication，少一个 i）
   # DB_HOST: str = "127.0.0.1"
    DB_HOST: str = "172.20.10.4"  # 改成你的电脑 IP
    DB_PORT: int = 3306

    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "garbage_classfication"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"  # 上传根目录
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}

    class Config:
        env_file = ".env"

settings = Settings()