from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    #  async pg
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    FE_BASE_URL: str
    BE_BASE_UR: str

    SHEET_ID: str

    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    class Config:
        env_file= ".env"
        env_file_encoding= "utf-8"
        extra= "ignore"

settings = Setting()