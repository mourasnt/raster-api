from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    RASTER_BASE_URL: str
    RASTER_AMBIENTE: str
    RASTER_LOGIN: str
    RASTER_SENHA: str
    RASTER_TIPO_RETORNO: str
    REDIS_HOST: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()