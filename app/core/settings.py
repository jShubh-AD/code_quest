from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    #  async pg
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    class Config:
        env_file= ".env"
        env_file_encoding= "utf-8"
        extra= "ignore"

settings = Setting()