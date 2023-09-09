from pydantic_settings import BaseSettings
from pydantic import SecretStr

class AppConfig(BaseSettings):
    USER_FROM: SecretStr
    USER_TO: SecretStr
    PASSWORD: SecretStr
    
    class Config:
        env_file = '.config'
        env_file_encoding = 'utf-8'


config = AppConfig()